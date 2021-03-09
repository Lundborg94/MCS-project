create table Device (
	Id uniqueidentifier primary key not null,
	Name nvarchar(100) not null,
	Color nvarchar(100) not null,
	Brand nvarchar(100) not null,
	Password nvarchar(100) not null
);

create table Cumulocity (
	DeviceId uniqueidentifier not null,
	Username nvarchar(100) not null,
	TenantId nvarchar(100) not null,
	Password nvarchar(100) not null,
	Active bit not null,

	constraint pk_Cumulocity primary key (DeviceId),
	constraint fk_Cumulocity_Device
		foreign key (DeviceId)
		references Device(Id)
		on delete cascade
);

create table Position (
	Id uniqueidentifier default newid() primary key not null,
	DeviceId uniqueidentifier not null,
	Latitude decimal(19,16) not null,
	Longitude decimal(19,16) not null,
	Altitude decimal(19,16) not null,
	CreatedDateTime datetime,

	constraint fk_Position_Device
		foreign key(DeviceId)
		references Device(Id)
		on delete cascade
);

create table EmergencyContact (
	Id uniqueidentifier default newid() primary key not null,
	DeviceId uniqueidentifier not null,
	Name nvarchar(100) not null,
	PhoneNumber nvarchar(100) not null,

	constraint fk_EmergencyContact_Device
		foreign key(DeviceId)
		references Device(Id)
		on delete cascade
);