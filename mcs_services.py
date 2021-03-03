import uuid

from mcs_repositories import DeviceRepositoryInterface, EmergencyRepositoryInterface


# DTOS
class DeviceDto:
    def __init__(self, device_id, name):
        self.id = device_id
        self.name = name


class UserDto:
    def __init__(self, device: DeviceDto):
        self.device = device


class EmergencyContactDto:
    def __init__(self, ec_id, phone_number):
        self.id = ec_id
        self.phone_number = phone_number


# SERVICES
class LoginService:
    def __init__(self, device_repo: DeviceRepositoryInterface):
        self._device_repo = device_repo

    def get_user(self, device_id: uuid):
        device_entity = self._device_repo.get_device(device_id)
        device = DeviceDto(device_entity.id, device_entity.name)
        return UserDto(device)

    def get_user_password(self, device_id: uuid):
        return self._device_repo.get_device(device_id).password


class DashboardService:
    def __init__(self, ice_repo: EmergencyRepositoryInterface):
        self._ice_repo = ice_repo

    def get_ice_contacts_for_device(self, device_id):
        ecs = self._ice_repo.get_emergency_contacts_for_device(device_id)
        return [EmergencyContactDto(ec.id, ec.phone_number) for ec in ecs]
