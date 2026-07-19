"""Atlas Runtime cognition layer.

The cognition layer fuses event streams into market context before state
transition. It does not trade, modify portfolios, or create CDE authority.

As of Runtime v1.6 the default decision pipeline is "lean"
(cognition_mode="lean"): event fusion + state controller + regime memory +
LLM decision + forecast ledger. The symbolic engines in this package
(causal intelligence, world model, latent structure, physics constraints,
market laws, unified intelligence, feedback / trust / hypothesis chain) run
only under cognition_mode="full" and are archived experimental layers with
controlled-fixture evidence only.
"""
