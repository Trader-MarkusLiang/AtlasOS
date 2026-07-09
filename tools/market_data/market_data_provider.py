"""Minimal market data provider utility for Atlas OS.

This module fetches market data for validation and Decision Brief support. It is not an Engine,
trading system, cache, crawler, or execution layer.
"""

from __future__ import annotations

import json
import multiprocessing as mp
import os
import queue
import signal
import threading
import urllib.parse
import urllib.request
from contextlib import contextmanager
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import pandas as pd


MISSING_VALUE = None
DEFAULT_PROVIDER_TIMEOUT_SECONDS = 4.0


def _safe_float(value: Any) -> Optional[float]:
    if value is None:
        return None
    try:
        if pd.isna(value):
            return None
        return float(value)
    except Exception:
        return None


def _market_to_yfinance_symbol(ticker: str, market: str) -> str:
    clean = str(ticker or "").strip().upper()
    base, suffix = _split_symbol(clean)
    if market == "HK" or suffix == "HK":
        normalized = "".join(ch for ch in base if ch.isdigit())[-4:].zfill(4)
        return f"{normalized}.HK"
    if market == "A-share" or suffix in {"SH", "SS", "SZ"}:
        normalized = base.zfill(6) if base.isdigit() else base
        if suffix == "SZ":
            return f"{normalized}.SZ"
        if suffix in {"SH", "SS"} or normalized.startswith(("6", "9")):
            return f"{normalized}.SS"
        return f"{normalized}.SZ"
    return clean


def _market_to_akshare_symbol(ticker: str, market: str) -> str:
    clean = str(ticker or "").strip().upper()
    base, suffix = _split_symbol(clean)
    if market == "HK" or suffix == "HK":
        normalized = "".join(ch for ch in base if ch.isdigit())[-5:].zfill(5)
        return normalized
    if market == "A-share" or suffix in {"SH", "SS", "SZ"}:
        return base.zfill(6) if base.isdigit() else base
    return clean


def _market_to_eastmoney_secid(ticker: str, market: str) -> str:
    clean = str(ticker or "").strip().upper()
    base, suffix = _split_symbol(clean)
    if market == "HK" or suffix == "HK":
        normalized = "".join(ch for ch in base if ch.isdigit())[-5:].zfill(5)
        return f"116.{normalized}"
    normalized = base.zfill(6) if base.isdigit() else base
    if market == "A-share" or suffix in {"SH", "SS", "SZ"}:
        exchange = "1" if suffix in {"SH", "SS"} or normalized.startswith(("6", "9")) else "0"
        return f"{exchange}.{normalized}"
    return clean


def _market_to_tencent_symbol(ticker: str, market: str) -> str:
    clean = str(ticker or "").strip().upper()
    base, suffix = _split_symbol(clean)
    if market == "HK" or suffix == "HK":
        normalized = "".join(ch for ch in base if ch.isdigit())[-5:].zfill(5)
        return f"hk{normalized}"
    normalized = base.zfill(6) if base.isdigit() else base
    if market == "A-share" or suffix in {"SH", "SS", "SZ"}:
        prefix = "sh" if suffix in {"SH", "SS"} or normalized.startswith(("6", "9")) else "sz"
        return f"{prefix}{normalized}"
    return clean.lower()


def _split_symbol(symbol: str) -> tuple[str, str]:
    if "." not in symbol:
        return symbol, ""
    base, suffix = symbol.rsplit(".", 1)
    return base, suffix


def _period_to_yfinance_period(period: str) -> str:
    if period.endswith("d"):
        try:
            days = int(period[:-1])
            if days <= 60:
                return "3mo"
            if days <= 120:
                return "6mo"
        except ValueError:
            pass
    return period


def _eastmoney_kline_history(ticker: str, market: str, period: str) -> pd.DataFrame:
    secid = _market_to_eastmoney_secid(ticker, market)
    if "." not in secid:
        raise ValueError(f"eastmoney does not support ticker={ticker!r} market={market!r}")
    params = {
        "secid": secid,
        "fields1": "f1,f2,f3,f4,f5,f6",
        "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61",
        "klt": "101",
        "fqt": "0",
        "beg": "0",
        "end": "20500101",
        "lmt": "160",
    }
    url = "https://push2his.eastmoney.com/api/qt/stock/kline/get?" + urllib.parse.urlencode(params)
    payload = _read_json_url(url)
    data = payload.get("data") if isinstance(payload, dict) else {}
    klines = data.get("klines") if isinstance(data, dict) else None
    if not isinstance(klines, list) or not klines:
        return pd.DataFrame()

    rows = []
    for raw in klines[-180:]:
        parts = str(raw or "").split(",")
        if len(parts) < 7:
            continue
        rows.append(
            {
                "date": pd.to_datetime(parts[0], errors="coerce"),
                "open": _safe_float(parts[1]),
                "close": _safe_float(parts[2]),
                "high": _safe_float(parts[3]),
                "low": _safe_float(parts[4]),
                "volume": _eastmoney_volume(parts[5], market),
                "turnover": _safe_float(parts[6]),
                "daily_change_pct": _safe_float(parts[8]) if len(parts) > 8 else None,
            }
        )
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    for col in ["open", "high", "low", "close", "volume", "turnover", "daily_change_pct"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["close"])
    df.attrs["source"] = "eastmoney_kline"
    return df


def _akshare_history(ticker: str, market: str, period: str) -> pd.DataFrame:
    import akshare as ak

    end_date = datetime.now().strftime("%Y%m%d")
    start_date = (datetime.now() - timedelta(days=220)).strftime("%Y%m%d")
    symbol = _market_to_akshare_symbol(ticker, market)

    if market == "A-share":
        df = ak.stock_zh_a_hist(
            symbol=symbol,
            period="daily",
            start_date=start_date,
            end_date=end_date,
            adjust="",
        )
    elif market == "HK":
        df = ak.stock_hk_hist(
            symbol=symbol,
            period="daily",
            start_date=start_date,
            end_date=end_date,
            adjust="",
        )
    else:
        raise ValueError(f"akshare does not support market={market!r} in this utility")

    if df is None or df.empty:
        return pd.DataFrame()

    rename_map = {
        "日期": "date",
        "收盘": "close",
        "开盘": "open",
        "最高": "high",
        "最低": "low",
        "成交量": "volume",
        "成交额": "turnover",
        "涨跌幅": "daily_change_pct",
    }
    df = df.rename(columns=rename_map)
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
    for col in ["open", "high", "low", "close", "volume", "turnover", "daily_change_pct"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def _yfinance_history(ticker: str, market: str, period: str) -> pd.DataFrame:
    import yfinance as yf

    symbol = _market_to_yfinance_symbol(ticker, market)
    df = yf.Ticker(symbol).history(period=_period_to_yfinance_period(period), interval="1d")
    if df is None or df.empty:
        return pd.DataFrame()

    df = df.reset_index()
    rename_map = {
        "Date": "date",
        "Open": "open",
        "High": "high",
        "Low": "low",
        "Close": "close",
        "Volume": "volume",
    }
    df = df.rename(columns=rename_map)
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
    for col in ["open", "high", "low", "close", "volume"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def _yahoo_chart_history(ticker: str, market: str, period: str) -> pd.DataFrame:
    symbol = _market_to_yfinance_symbol(ticker, market)
    chart_range = _period_to_yfinance_period(period)
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range={chart_range}&interval=1d"
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(request, timeout=min(8.0, _provider_attempt_timeout_seconds())) as response:
        payload = json.loads(response.read().decode("utf-8") or "{}")
    chart = payload.get("chart") if isinstance(payload, dict) else {}
    if not isinstance(chart, dict) or chart.get("error"):
        return pd.DataFrame()
    results = chart.get("result")
    if not isinstance(results, list) or not results:
        return pd.DataFrame()
    first = results[0] if isinstance(results[0], dict) else {}
    timestamps = first.get("timestamp") if isinstance(first.get("timestamp"), list) else []
    quote = first.get("indicators", {}).get("quote", [{}])
    quote = quote[0] if isinstance(quote, list) and quote and isinstance(quote[0], dict) else {}
    rows = []
    for index, stamp in enumerate(timestamps):
        rows.append(
            {
                "date": pd.to_datetime(stamp, unit="s", utc=True, errors="coerce"),
                "open": _safe_index(quote.get("open"), index),
                "high": _safe_index(quote.get("high"), index),
                "low": _safe_index(quote.get("low"), index),
                "close": _safe_index(quote.get("close"), index),
                "volume": _safe_index(quote.get("volume"), index),
            }
        )
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    for col in ["open", "high", "low", "close", "volume"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["close"])
    df.attrs["source"] = "yahoo_chart"
    return df


def get_history(ticker: str, market: str, period: str = "60d") -> pd.DataFrame:
    """Return recent daily history with normalized columns where possible."""

    if not ticker:
        return pd.DataFrame()

    attempts: list[str] = []
    if market in {"A-share", "HK"}:
        attempts.append("eastmoney_kline")
        attempts.append("akshare")
    if market in {"A-share", "HK", "US", "US / ETF", "ETF"}:
        attempts.append("yfinance")
        attempts.append("yahoo_chart")

    errors: List[str] = []
    for source in attempts:
        try:
            df = _load_history_with_deadline(source, ticker, market, period)
            if df is not None and not df.empty:
                df.attrs["source"] = source
                return df
            errors.append(f"{source}: empty")
        except Exception as exc:
            errors.append(f"{source}: {type(exc).__name__}: {exc}")

    df = pd.DataFrame()
    df.attrs["errors"] = errors
    return df


def _run_history_loader(source: str, ticker: str, market: str, period: str) -> pd.DataFrame:
    if source == "eastmoney_kline":
        return _eastmoney_kline_history(ticker, market, period)
    if source == "akshare":
        return _akshare_history(ticker, market, period)
    if source == "yfinance":
        return _yfinance_history(ticker, market, period)
    if source == "yahoo_chart":
        return _yahoo_chart_history(ticker, market, period)
    raise ValueError(f"unknown market data source: {source}")


def _load_history_with_deadline(source: str, ticker: str, market: str, period: str) -> pd.DataFrame:
    if _hard_timeout_enabled(source):
        return _load_history_in_process(source, ticker, market, period)
    with _provider_attempt_deadline(source):
        return _run_history_loader(source, ticker, market, period)


def _hard_timeout_enabled(source: str) -> bool:
    raw = os.environ.get("ATLAS_MARKET_PROVIDER_HARD_TIMEOUT", "1").strip().lower()
    return raw not in {"0", "false", "no", "off"} and source in {"akshare", "yfinance"}


def _load_history_in_process(source: str, ticker: str, market: str, period: str) -> pd.DataFrame:
    seconds = _provider_attempt_timeout_seconds()
    ctx = mp.get_context("fork") if "fork" in mp.get_all_start_methods() else mp.get_context()
    result_queue = ctx.Queue(maxsize=1)
    process = ctx.Process(target=_history_worker, args=(source, ticker, market, period, result_queue))
    process.daemon = True
    process.start()
    process.join(seconds)
    if process.is_alive():
        process.terminate()
        process.join(1)
        if process.is_alive() and hasattr(process, "kill"):
            process.kill()
            process.join(1)
        raise TimeoutError(f"{source} timed out after {seconds:.2f}s")
    try:
        result = result_queue.get_nowait()
    except queue.Empty as exc:
        raise RuntimeError(f"{source} exited without result") from exc
    if not isinstance(result, dict):
        raise RuntimeError(f"{source} returned malformed result")
    if result.get("ok"):
        df = result.get("data")
        return df if isinstance(df, pd.DataFrame) else pd.DataFrame()
    raise RuntimeError(str(result.get("error") or f"{source} failed"))


def _history_worker(source: str, ticker: str, market: str, period: str, result_queue: Any) -> None:
    try:
        result_queue.put({"ok": True, "data": _run_history_loader(source, ticker, market, period)})
    except Exception as exc:
        result_queue.put({"ok": False, "error": f"{type(exc).__name__}: {exc}"})


def _provider_attempt_timeout_seconds() -> float:
    raw = os.environ.get("ATLAS_MARKET_PROVIDER_TIMEOUT_SECONDS")
    if raw is None:
        return DEFAULT_PROVIDER_TIMEOUT_SECONDS
    try:
        value = float(raw)
    except ValueError:
        return DEFAULT_PROVIDER_TIMEOUT_SECONDS
    return max(0.25, value)


@contextmanager
def _provider_attempt_deadline(source: str):
    seconds = _provider_attempt_timeout_seconds()
    if threading.current_thread() is not threading.main_thread():
        yield
        return

    def _handle_timeout(_signum: int, _frame: Any) -> None:
        raise TimeoutError(f"{source} timed out after {seconds:.2f}s")

    previous_handler = signal.getsignal(signal.SIGALRM)
    previous_timer = signal.setitimer(signal.ITIMER_REAL, 0)
    signal.signal(signal.SIGALRM, _handle_timeout)
    signal.setitimer(signal.ITIMER_REAL, seconds)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous_handler)
        if previous_timer[0] > 0:
            signal.setitimer(signal.ITIMER_REAL, previous_timer[0], previous_timer[1])


def _pct_change_from_tail(df: pd.DataFrame, periods: int) -> Optional[float]:
    if df.empty or "close" not in df.columns or len(df) <= periods:
        return None
    latest = _safe_float(df["close"].iloc[-1])
    previous = _safe_float(df["close"].iloc[-(periods + 1)])
    if latest is None or previous in (None, 0):
        return None
    return (latest / previous - 1.0) * 100.0


def get_latest_quote(ticker: str, market: str) -> Dict[str, Any]:
    """Return latest quote fields from current history snapshot."""

    snapshot = get_market_snapshot(ticker, market)
    return {
        key: snapshot.get(key)
        for key in [
            "ticker",
            "market",
            "source",
            "timestamp",
            "latest_price",
            "daily_change_pct",
            "volume",
            "turnover",
            "data_status",
            "missing_fields",
        ]
    }


def get_market_snapshot(ticker: str, market: str) -> Dict[str, Any]:
    """Return a normalized market snapshot.

    Valuation fields are optional and may remain missing.
    """

    result: Dict[str, Any] = {
        "ticker": ticker,
        "market": market,
        "source": None,
        "timestamp": None,
        "latest_price": None,
        "daily_change_pct": None,
        "volume": None,
        "turnover": None,
        "change_5d_pct": None,
        "change_20d_pct": None,
        "change_60d_pct": None,
        "ma20": None,
        "ma60": None,
        "market_cap": None,
        "pe": None,
        "pb": None,
        "data_status": "Unavailable",
        "missing_fields": [],
        "errors": [],
    }

    if not ticker:
        result["errors"].append("Ticker missing")
        result["missing_fields"] = _missing_fields(result)
        return result

    history = get_history(ticker, market, "60d")
    result["source"] = history.attrs.get("source")
    result["errors"] = history.attrs.get("errors", [])

    if history.empty:
        fallback = _quote_fallback_snapshot(ticker, market, errors=result["errors"])
        if fallback:
            result.update(fallback)
            result["missing_fields"] = _missing_fields(result)
            result["data_status"] = _data_status(result)
            return result
        result["missing_fields"] = _missing_fields(result)
        return result

    row = history.iloc[-1]
    result["timestamp"] = _timestamp_to_iso(row.get("date"))
    result["latest_price"] = _safe_float(row.get("close"))
    result["daily_change_pct"] = _safe_float(row.get("daily_change_pct"))
    if result["daily_change_pct"] is None:
        result["daily_change_pct"] = _pct_change_from_tail(history, 1)
    result["volume"] = _safe_float(row.get("volume"))
    result["turnover"] = _safe_float(row.get("turnover"))
    result["change_5d_pct"] = _pct_change_from_tail(history, 5)
    result["change_20d_pct"] = _pct_change_from_tail(history, 20)
    result["change_60d_pct"] = _pct_change_from_tail(history, 60)
    result["ma20"] = _moving_average(history, 20)
    result["ma60"] = _moving_average(history, 60)

    result["missing_fields"] = _missing_fields(result)
    result["data_status"] = _data_status(result)
    return result


def _quote_fallback_snapshot(ticker: str, market: str, errors: List[str]) -> Optional[Dict[str, Any]]:
    quote_errors = list(errors)
    for source, loader in (
        ("eastmoney_quote", _eastmoney_quote_snapshot),
        ("tencent_quote", _tencent_quote_snapshot),
    ):
        try:
            snapshot = loader(ticker, market)
        except Exception as exc:
            quote_errors.append(f"{source}: {type(exc).__name__}: {exc}")
            continue
        if snapshot and snapshot.get("latest_price") is not None:
            snapshot["errors"] = quote_errors
            return snapshot
        quote_errors.append(f"{source}: empty")
    return None


def _eastmoney_quote_snapshot(ticker: str, market: str) -> Optional[Dict[str, Any]]:
    secid = _market_to_eastmoney_secid(ticker, market)
    if "." not in secid:
        return None
    params = {
        "secid": secid,
        "fields": "f43,f44,f45,f46,f47,f48,f57,f58,f116,f117,f162,f167,f170",
    }
    url = "https://push2.eastmoney.com/api/qt/stock/get?" + urllib.parse.urlencode(params)
    payload = _read_json_url(url)
    data = payload.get("data") if isinstance(payload, dict) else {}
    if not isinstance(data, dict):
        return None
    price_scale = 1000.0 if market == "HK" or str(ticker).upper().endswith(".HK") else 100.0
    return {
        "ticker": ticker,
        "market": market,
        "source": "eastmoney_quote",
        "timestamp": _quote_timestamp(),
        "latest_price": _scaled(data.get("f43"), price_scale),
        "daily_change_pct": _scaled(data.get("f170"), 100.0),
        "volume": _eastmoney_volume(data.get("f47"), market),
        "turnover": _safe_float(data.get("f48")),
        "market_cap": _safe_float(data.get("f116")),
        "pe": _scaled(data.get("f162"), 100.0),
        "pb": _scaled(data.get("f167"), 100.0),
    }


def _tencent_quote_snapshot(ticker: str, market: str) -> Optional[Dict[str, Any]]:
    symbol = _market_to_tencent_symbol(ticker, market)
    if not symbol:
        return None
    url = f"https://qt.gtimg.cn/q={urllib.parse.quote(symbol)}"
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(request, timeout=min(6.0, _provider_attempt_timeout_seconds())) as response:
        body = response.read().decode("gbk", "ignore")
    if "~" not in body:
        return None
    raw = body.split('"', 1)[1].rsplit('"', 1)[0] if '"' in body else body
    parts = raw.split("~")
    if len(parts) < 35:
        return None
    volume = _safe_float(_safe_part(parts, 6))
    turnover = None
    packed = str(_safe_part(parts, 35) or "") if len(parts) > 35 else ""
    if "/" in packed:
        packed_parts = packed.split("/")
        if len(packed_parts) >= 3:
            turnover = _safe_float(packed_parts[2])
    if turnover is None and len(parts) > 37:
        turnover = _safe_float(_safe_part(parts, 37))
    return {
        "ticker": ticker,
        "market": market,
        "source": "tencent_quote",
        "timestamp": _quote_timestamp(_safe_part(parts, 30)),
        "latest_price": _safe_float(_safe_part(parts, 3)),
        "daily_change_pct": _safe_float(_safe_part(parts, 32)),
        "volume": _tencent_volume(volume, symbol),
        "turnover": turnover,
    }


def _timestamp_to_iso(value: Any) -> Optional[str]:
    if value is None or pd.isna(value):
        return None
    try:
        return pd.Timestamp(value).isoformat()
    except Exception:
        return str(value)


def _safe_index(values: Any, index: int) -> Any:
    if isinstance(values, list) and index < len(values):
        return values[index]
    return None


def _safe_part(parts: List[str], index: int) -> Optional[str]:
    return parts[index] if index < len(parts) else None


def _read_json_url(url: str) -> Dict[str, Any]:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://quote.eastmoney.com/",
            "Accept": "application/json,text/plain,*/*",
        },
    )
    with urllib.request.urlopen(request, timeout=min(6.0, _provider_attempt_timeout_seconds())) as response:
        return json.loads(response.read().decode("utf-8") or "{}")


def _scaled(value: Any, scale: float) -> Optional[float]:
    number = _safe_float(value)
    if number is None:
        return None
    return number / scale


def _eastmoney_volume(value: Any, market: str) -> Optional[float]:
    volume = _safe_float(value)
    if volume is None:
        return None
    return volume if market == "HK" else volume * 100.0


def _tencent_volume(value: Optional[float], symbol: str) -> Optional[float]:
    if value is None:
        return None
    return value * 100.0 if str(symbol).startswith("sz") else value


def _quote_timestamp(value: Any = None) -> str:
    parsed = pd.to_datetime(value, errors="coerce") if value else pd.NaT
    if parsed is not pd.NaT and not pd.isna(parsed):
        return pd.Timestamp(parsed).isoformat()
    return datetime.utcnow().isoformat() + "Z"


def _moving_average(df: pd.DataFrame, window: int) -> Optional[float]:
    if df.empty or "close" not in df.columns or len(df) < window:
        return None
    return _safe_float(df["close"].tail(window).mean())


def _missing_fields(result: Dict[str, Any]) -> List[str]:
    required = [
        "source",
        "timestamp",
        "latest_price",
        "daily_change_pct",
        "volume",
        "turnover",
        "change_5d_pct",
        "change_20d_pct",
        "change_60d_pct",
        "ma20",
        "ma60",
    ]
    optional = ["market_cap", "pe", "pb"]
    missing = [field for field in required if result.get(field) is None]
    missing.extend([f"{field} (optional)" for field in optional if result.get(field) is None])
    return missing


def _data_status(result: Dict[str, Any]) -> str:
    core_fields = ["source", "timestamp", "latest_price", "volume"]
    if all(result.get(field) is not None for field in core_fields):
        if result.get("change_20d_pct") is not None and result.get("ma20") is not None:
            return "Available"
        return "Partial"
    if result.get("latest_price") is not None:
        return "Partial"
    return "Unavailable"
