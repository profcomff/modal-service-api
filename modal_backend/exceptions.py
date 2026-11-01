from typing import Type


class ModalApiError(Exception):
    eng: str
    ru: str

    def __init__(self, eng: str, ru: str) -> None:
        self.eng = eng
        self.ru = ru
        super().__init__(eng)


class ObjectNotFound(ModalApiError):
    def __init__(self, obj: type, obj_id_or_name: int | str):
        super().__init__(
            f"Object {obj.__name__} {obj_id_or_name=} not found",
            f"Объект {obj.__name__} с идентификатором {obj_id_or_name} не найден",
        )


class AlreadyExists(ModalApiError):
    def __init__(self, obj: type, obj_id_or_name: int | str):
        super().__init__(
            f"Object {obj.__name__}, {obj_id_or_name=} already exists",
            f"Объект {obj.__name__} с идентификатором {obj_id_or_name=} уже существует",
        )


class InvalidStatusTransition(ModalApiError):
    """An archive/restore request is inconsistent with the current status."""

    def __init__(self, current_status: str):
        if current_status == "archived":
            eng = "Notification is already archived"
            ru = "Модалка уже в архиве"
        elif current_status == "active":
            eng = "Notification is already active"
            ru = "Модалка уже активна"
        else:
            eng = f"Invalid notification status transition from {current_status}"
            ru = f"Недопустимый переход статуса модалки из {current_status}"
        super().__init__(eng, ru)


class ForbiddenAction(ModalApiError):
    def __init__(self, type: Type):
        super().__init__(f"Forbidden action with {type.__name__}", f"Запрещенное действие с объектом {type.__name__}")


class ValueError(ModalApiError):
    def __init__(self, value: str):
        super().__init__(f"Value {value} is not valid", f"Значение {value} недопустимо")
