import sqlite3
import uuid
import datetime
import cumulocity_api
import pyodbc


# ENTITIES
class EmergencyContact:
    def __init__(self, id, device_id: uuid, phone_number: str, name):
        self.id = id
        self.device_id = device_id
        self.phone_number = phone_number
        self.name = name


class Device:
    def __init__(self, id: uuid, name: str, password: str, vehicle_color, vehicle_brand):
        self.id = id
        self.name = name
        self.password = password
        self.vehicle_color = vehicle_color
        self.vehicle_brand = vehicle_brand


# INTERFACES
class DeviceRepositoryInterface:
    """
    Device repository interface.
    All adaptors should inherit this class.
    """

    def get_device(self, id: uuid) -> Device:
        """Fetches a device with the specified id from current context"""
        raise NotImplementedError()

    def add_device(self, id: uuid, name: str, password, color, brand):
        """Adds a device to current context"""
        raise NotImplementedError()

    def remove_device(self, id: uuid):
        """Removes a device from the current context"""
        raise NotImplementedError()


class EmergencyRepositoryInterface:

    def get_emergency_contact(self, id):
        """Fetches an emergency contact from the current context"""
        raise NotImplementedError()

    def get_emergency_contacts_for_device(self, device_id: uuid) -> list[EmergencyContact]:
        """Fetches emergency contacts for specified device"""
        raise NotImplementedError()

    def add_emergency_contact(self, device_id: uuid, phone_number: str, name) -> int:
        """Adds an emergency contact to the current context. Returns the assigned contact id."""
        raise NotImplementedError()

    def remove_emergency_contact(self, id: int):
        """Removes an emergency contact from the current context"""
        raise NotImplementedError()

    def device_has_contact_id(self, device_id, ec_id):
        """Checks if the specified emergency contact exists for the specified device. Return true if it exists otherwise
         false"""
        raise NotImplementedError()


# ADAPTORS
class DeviceRepositoryTest(DeviceRepositoryInterface):
    """
    For testing against our sqlite db
    """

    def __init__(self, sqlite_connection: sqlite3.Connection):
        self.__context = sqlite_connection
        self.__context.execute('PRAGMA foreign_keys = ON')  # For cascade deletion and restrictions

    def get_device(self, id: uuid):
        cursor = self.__context.execute('SELECT * FROM Device WHERE Id = ?', [str(id)])

        tup = cursor.fetchone()

        if not tup:
            return None

        device_id, name, color, brand, password, _ = tup
        device = Device(id=device_id, name=name, password=password, vehicle_color=color, vehicle_brand=brand)

        return device

    def add_device(self, id: uuid, name: str, password: str, color, brand):
        self.__context.execute('INSERT INTO Device VALUES (?, ?, ?, ?, ?, NULL)', [str(id), name, color, brand, password])
        self.__context.commit()

    def remove_device(self, id: uuid):
        self.__context.execute('DELETE FROM Device WHERE Id = ?', [str(id)])
        self.__context.commit()
        

class DeviceRepository(DeviceRepositoryInterface):
    def __init__(self, context: pyodbc.Connection):
        self.__context = context

    def get_device(self, id: uuid) -> Device:
        cursor = self.__context.execute('select * from Device where Id = ?', str(id))
        tup = cursor.fetchone()
        if not tup:
            return None
        device_id, device_name, vehicle_color, vehicle_brand, password = tup
        return Device(
            id=device_id,
            name=device_name,
            vehicle_color=vehicle_color,
            vehicle_brand=vehicle_brand,
            password=password)

    def add_device(self, id: uuid, name: str, password, color, brand):
        self.__context.execute("""
            insert into Device (Id, Name, Color, Brand, Password)
            values (?, ?, ?, ?, ?)
        """, [str(id), name, color, brand, password])
        self.__context.commit()

    def remove_device(self, id: uuid):
        self.__context.execute('delete Device where Id = ?', str(id))
        self.__context.commit()


class EmergencyRepositoryTest(EmergencyRepositoryInterface):

    def __init__(self, sqlite_connection: sqlite3.Connection):
        self.__context = sqlite_connection
        self.__context.execute('PRAGMA foreign_keys = ON')  # For cascade deletion and restrictions

    def get_emergency_contact(self, id):
        cursor = self.__context.execute('SELECT * FROM EmergencyContact WHERE Id = ?', [id])
        tup = cursor.fetchone()

        if not tup:
            return None

        ec_id, d_id, name, phone_number = tup
        ec = EmergencyContact(id=ec_id, device_id=d_id, name=name, phone_number=phone_number)
        return ec

    def get_emergency_contacts_for_device(self, device_id: uuid) -> list[EmergencyContact]:
        cursor = self.__context.execute('SELECT * FROM EmergencyContact WHERE DeviceId = ?', [device_id])
        tups = cursor.fetchall()
        return [EmergencyContact(id=ec_id, device_id=d_id, name=name, phone_number=phone_number) for ec_id, d_id, name, phone_number in tups]

    def add_emergency_contact(self, device_id: uuid, phone_number: str, name):
        cursor = self.__context.execute('INSERT INTO EmergencyContact VALUES (NULL, ?, ?, ?)',
                                        [str(device_id), name, phone_number])
        ec_id = cursor.lastrowid
        self.__context.commit()
        return ec_id

    def remove_emergency_contact(self, id: int):
        self.__context.execute('DELETE FROM EmergencyContact WHERE Id = ?', [id])
        self.__context.commit()

    def device_has_contact_id(self, device_id, ec_id):
        cursor = self.__context.execute("""
            SELECT 1
            FROM EmergencyContact ec
            JOIN Device d ON ec.DeviceId = d.Id
            WHERE d.Id = ? AND ec.Id = ?
        """, [str(device_id), str(ec_id)])

        if not cursor.fetchone():
            return False

        return True


class EmergencyRepository(EmergencyRepositoryInterface):
    def __init__(self, context: pyodbc.Connection):
        self.__context = context

    def get_emergency_contact(self, id):
        cursor = self.__context.execute('select * from EmergencyContact where Id = ?', str(id))
        tup = cursor.fetchone()
        if not tup:
            return None
        ec_id, device_id, name, phone_number = tup
        return EmergencyContact(id=ec_id, device_id=device_id, name=name, phone_number=phone_number)

    def get_emergency_contacts_for_device(self, device_id: uuid) -> list[EmergencyContact]:
        cursor = self.__context.execute('select * from EmergencyContact where DeviceId = ?', str(device_id))
        tups = cursor.fetchall()
        return [EmergencyContact(id=ec_id, device_id=device_id, name=name, phone_number=phone_number)
                for ec_id, device_id, name, phone_number in tups]

    def add_emergency_contact(self, device_id: uuid, phone_number: str, name) -> uuid:
        cursor = self.__context.execute("""
            insert into EmergencyContact (DeviceId, Name, PhoneNumber)
            output inserted.Id
            values (?, ?, ?)
        """, [str(device_id), name, phone_number])
        generated_id = cursor.fetchone()[0]  # Retrieve the id of the contact that was just created
        self.__context.commit()
        return generated_id

    def remove_emergency_contact(self, id: int):
        self.__context.execute('delete EmergencyContact where Id = ?', str(id))
        self.__context.commit()

    def device_has_contact_id(self, device_id, ec_id):
        cursor = self.__context.execute("""
            select 1
            from EmergencyContact ec
            join Device d on ec.DeviceId = d.Id
            where d.Id = ? and ec.Id = ?
        """, [str(device_id), str(ec_id)])
        tup = cursor.fetchone()
        if not tup:
            return False
        return True


class CumulocityRepositoryTest:

    def __init__(self, sqlite_connection: sqlite3.Connection):
        self.__context = sqlite_connection
        self.__context.execute('PRAGMA foreign_keys = ON')  # For cascade deletion and restrictions

    def get_active_cumulocity_device(self):
        cursor = self.__context.execute("""
            SELECT
                d.Id,
                c.Username,
                c.TenantId,
                c.Password
            FROM Device d
            JOIN Cumulocity c ON d.CumulocityId = c.Id
            WHERE c.Active == 1
        """)

        return cursor.fetchall()

    def add_cumulocity(self, cumulocity_username, cumulocity_tenant_id, cumulocity_password, user_id, active):
        cursor = self.__context.execute('INSERT INTO Cumulocity VALUES (null, ?, ?, ?, ?)',
                               [cumulocity_username, cumulocity_tenant_id, cumulocity_password, active])
        cumulocity_id = cursor.lastrowid
        self.__context.commit()

        self.__context.execute('UPDATE Device SET CumulocityId = ? WHERE Id = ?', [cumulocity_id, str(user_id)])
        self.__context.commit()

    def set_state(self, device_id, state: bool):
        cursor = self.__context.execute('SELECT CumulocityId FROM Device WHERE Id = ?', [str(device_id)])
        c_id, = cursor.fetchone()
        self.__context.execute('UPDATE Cumulocity SET Active = ? WHERE Id = ?', [state, c_id])
        self.__context.commit()

    def get_realtime_location(self, device_id):
        context = self.__context.execute("""
            SELECT
                c.Username,
                c.TenantId,
                c.Password
            FROM Device d
            JOIN Cumulocity c on d.CumulocityId = c.Id
            WHERE d.Id = ?
        """, [str(device_id)])

        username, tenant_id, password = context.fetchone()

        return cumulocity_api.get_location(username, tenant_id, password)


class CumulocityRepository:
    def __init__(self, context: pyodbc.Connection):
        self.__context = context

    def get_active_cumulocity_device(self):
        cursor = self.__context.execute("""
            select
                DeviceId,
                Username,
                TenantId,
                Password
            from Cumulocity
            where Active = 1
        """)
        return cursor.fetchall()

    def add_cumulocity(self, cumulocity_username, cumulocity_tenant_id, cumulocity_password, user_id, active):
        self.__context.execute("""
            insert into Cumulocity (DeviceId, Username, TenantId, Password, Active)
            values (?, ?, ?, ?, ?)
        """, [str(user_id), cumulocity_username, cumulocity_tenant_id, cumulocity_password, active])
        self.__context.commit()

    def set_state(self, device_id, state: bool):
        self.__context.execute('update Cumulocity set Active = ? where DeviceId = ?', [state, str(device_id)])
        self.__context.commit()

    def get_realtime_location(self, device_id):
        context = self.__context.execute('select Username, TenantId, Password from Cumulocity where DeviceId = ?',
                                         str(device_id))
        tup = context.fetchone()
        if not tup:
            return None
        username, tenant_id, password = tup
        return cumulocity_api.get_location(username, tenant_id, password)


class LocationRepositoryTest:

    def __init__(self, sqlite_connection: sqlite3.Connection):
        self.__context = sqlite_connection
        self.__context.execute('PRAGMA foreign_keys = ON')

    def add_location(self, device_id, latitude, longitude, altitude):
        self.__context.execute('INSERT INTO Position VALUES (NULL, ?, ?, ?, ?, ?)',
                               [str(device_id), latitude, longitude, altitude, datetime.datetime.utcnow()])
        self.__context.commit()

    def get_latest_location(self, device_id):
        cursor = self.__context.execute("""
            SELECT
                p.Latitude,
                p.Longitude,
                p.Altitude,
                p.CreatedDateTime
            FROM Position p
            WHERE p.DeviceId = ?
            ORDER BY p.CreatedDateTime DESC
            LIMIT 1
        """, [str(device_id)])

        tup = cursor.fetchone()

        if not tup:
            return None

        return {
            "latitude": tup[0],
            "longitude": tup[1],
            "altitude": tup[2],
            "date_time": tup[3]
        }


class LocationRepository:
    def __init__(self, context: pyodbc.Connection):
        self.__context = context

    def add_location(self, device_id, latitude, longitude, altitude):
        self.__context.execute("""
            insert into Position (DeviceId, Latitude, Longitude, Altitude, CreatedDateTime)
            values (?, ?, ?, ?, ?)
        """, [str(device_id), latitude, longitude, altitude, datetime.datetime.utcnow()])
        self.__context.commit()

    def get_latest_location(self, device_id):
        cursor = self.__context.execute("""
            select top(1)
                Longitude,
                Latitude,
                Altitude,
                CreatedDateTime
            from Position
            where DeviceId = ?
            order by CreatedDateTime desc
        """, str(device_id))
        tup = cursor.fetchone()
        if not tup:
            return None

        longitude, latitude, altitude, created_date_time = tup
        return {
            "longitude": longitude,
            "latitude": latitude,
            "altitude": altitude,
            "date_time": created_date_time
        }

