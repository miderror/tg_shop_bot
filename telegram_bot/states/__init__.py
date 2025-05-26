from aiogram.fsm.state import State, StatesGroup


class CartStates(StatesGroup):
    waiting_for_quantity = State()


class OrderStates(StatesGroup):
    waiting_for_delivery_info = State()
