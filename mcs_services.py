import uuid

from mcs_repositories import DeviceRepositoryInterface, EmergencyRepositoryInterface, CumulocityRepository


# DTOS
class DeviceDto:
    def __init__(self, device_id, name):
        self.id = device_id
        self.name = name


class UserDto:
    def __init__(self, device: DeviceDto):
        self.device = device


class AddUserDto:
    def __init__(self, device_id: uuid, device_name, password, cumulocity_name, cumulocity_tenant_id, cumulocity_password):
        self.device_id = device_id
        self.device_name = device_name
        self.password = password
        self.cumulocity_name = cumulocity_name
        self.cumulocity_tenant_id = cumulocity_tenant_id
        self.cumulocity_password = cumulocity_password


class EmergencyContactDto:
    def __init__(self, ec_id, phone_number):
        self.id = ec_id
        self.phone_number = phone_number


# SERVICES
class AccountService:
    def __init__(self, device_repo: DeviceRepositoryInterface, cumulocity_repo: CumulocityRepository):
        self._device_repo = device_repo
        self._cumulocity_repo = cumulocity_repo

    def add_user(self, user: AddUserDto):
        """Adds the user to the repository."""
        self._device_repo.add_device(user.device_id, user.device_name, user.password)
        self._cumulocity_repo.add_cumulocity(user.cumulocity_name, user.cumulocity_tenant_id, user.cumulocity_password, user.device_id)

    def get_user(self, device_id: uuid):
        """Returns the specified user from the repository. Returns 'None' if the user does not exist."""
        device_entity = self._device_repo.get_device(device_id)
        if not device_entity:
            return None
        device = DeviceDto(device_entity.id, device_entity.name)
        return UserDto(device)

    def get_user_password(self, device_id: uuid):
        """Returns the password of the specified user."""
        return self._device_repo.get_device(device_id).password


class DashboardService:
    def __init__(self, ice_repo: EmergencyRepositoryInterface):
        self._ice_repo = ice_repo

    def get_ice_contacts_for_device(self, device_id):
        """Returns all ice contacts for the current device/user"""
        ecs = self._ice_repo.get_emergency_contacts_for_device(device_id)
        return [EmergencyContactDto(ec.id, ec.phone_number) for ec in ecs]
