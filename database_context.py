import sqlite3
import uuid


# ENTITIES
class EmergencyContact:
    def __init__(self, phone_number: str):
        self.phone_number = phone_number


class Device:
    def __init__(self, id: uuid, name: str, emergency_contacts: list[EmergencyContact] = []):
        self.id = id
        self.name = name
        self.emergency_contacts = emergency_contacts


# INTERFACES
class DeviceDbContextInterface:
    """
    Database context interface
    """

    def get_device_password(self, device_id: uuid):
        """Fetches the password for specified device from current context"""
        raise NotImplementedError()

    def get_device(self, id: uuid):
        """Fetches a device with the specified id from current context"""
        raise NotImplementedError()

    def add_device(self, device: Device):
        """Adds a device to current context"""
        raise NotImplementedError()

    def remove_device(self, id: uuid):
        """Removes a device from the current context"""
        raise NotImplementedError()


# ADAPTORS
class DeviceTestContext(DeviceDbContextInterface):
    def __init__(self, sqlite_connection: sqlite3.Connection):
        self.__sqlite_connection = sqlite_connection

    def get_device_password(self, device_id: uuid):
        query = self.__sqlite_connection.execute("SELECT Password FROM Device WHERE Id = ?", [str(device_id)])
        return query.fetchone()[0]

    def get_device(self, id: uuid):
        query = self.__sqlite_connection.execute("""
            SELECT
                d.Id, d.Name, ec.PhoneNumber
            FROM Device d
            JOIN EmergencyContact ec on d.Id = ec.DeviceId
            WHERE d.Id = ?
        """, [str(id)])

        cursor = query.fetchall()

        device = Device(id, cursor[0][1])
        for tup in cursor:
            device.emergency_contacts.append(EmergencyContact(phone_number=tup[2]))

        return device

    def add_device(self, device):
        pass  # TODO: Implement

    def remove_device(self, id: uuid):
        pass  # TODO: Implement
