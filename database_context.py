import sqlite3
import uuid


# INTERFACES
class MCSDbContextInterface:
    """
    Database context interface
    """

    def get_user(self, id):
        """Fetches a user with the specified id from current context"""
        raise NotImplementedError()

    def get_user_password(self, user_id):
        """Fetches the password for specified user from current context"""
        raise NotImplementedError()

    def add_user(self, user):
        """Adds a user to current context"""
        raise NotImplementedError()

    def get_device(self, id):
        """Fetches a device with the specified id from current context"""
        raise NotImplementedError()

    def add_device(self, device, user_id):
        """Adds a device to current context"""
        raise NotImplementedError()


# ENTITIES
class EmergencyContact:
    def __init__(self, id: int, device_id: uuid, phone_number: str):
        self.id = id
        self.device_id = device_id
        self.phone_number = phone_number


class Device:
    def __init__(self, id: uuid, user_id: int, name: str, emergency_contacts: list[EmergencyContact] = []):
        self.id = id
        self.user_id = user_id
        self.name = name
        self.emergency_contacts = emergency_contacts


class User:
    def __init__(self, id: int, name: str, devices: list[Device] = []):
        self.id = id
        self.name = name
        self.devices = devices


# ADAPTORS
class MCSTestContext(MCSDbContextInterface):
    def __init__(self, sqlite_connection: sqlite3.Connection):
        self.sqlite_connection = sqlite_connection

    def get_user(self, id):
        query = self.sqlite_connection.execute("""
            SELECT
                u.Id,
                u.Name,
                d.Id,
                d.Name,
                ec.Id,
                ec.PhoneNumber
            FROM User u
            JOIN Device d ON u.Id = d.UserId
            JOIN EmergencyContact ec ON d.Id = ec.DeviceId
            WHERE U.Id = ?
        """, [id])

        table = query.fetchall()

        user = User(id, table[0][1])

        # Following code aggregates table rows into an object

        device_set = set()
        for tup in table:
            device_set.add((tup[2], tup[3]))

        for ds in device_set:
            device_id = ds[0]
            device_name = ds[1]
            device = Device(device_id, id, device_name, [])
            for tup in table:
                if tup[2] == device_id:
                    ec_id = tup[4]
                    phone_number = tup[5]
                    device.emergency_contacts.append(EmergencyContact(ec_id, device_id, phone_number))
            user.devices.append(device)

        return user

    def get_user_password(self, user_id):
        table = self.sqlite_connection.execute("SELECT Password FROM User WHERE Id = ?", [user_id])
        return table.fetchone()[0]

    def add_user(self, user):
        return super().add_user(user)

    def get_device(self, id):
        device = self.sqlite_connection.execute("""
            SELECT *
            FROM Device d
            JOIN EmergencyContact ec ON d.Id = ec.DeviceId
            WHERE d.Id = ?
        """, [id])

    def add_device(self, device, user_id):
        return super().add_device(device, user_id)
