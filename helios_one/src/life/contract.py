class Contract:
    def __init__(self, payer_id, payee_id, amount, trigger_tick, condition=None):
        self.payer_id = payer_id
        self.payee_id = payee_id
        self.amount = amount
        self.trigger_tick = trigger_tick
        self.condition = condition # e.g., "if_alive"
        self.status = 'PENDING' # PENDING, FULFILLED, FAILED, VOID
        self.enforcer_id = None # Gate 54.2: The Sheriff
