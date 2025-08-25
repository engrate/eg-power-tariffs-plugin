CREATE TABLE providers (
	active bool NOT NULL,
	ediel int4 NOT NULL,
	uid uuid NOT NULL,
	org_number varchar(50) NOT NULL,
	"name" varchar(255) NOT NULL,
	CONSTRAINT providers_ediel_key UNIQUE (ediel),
	CONSTRAINT providers_name_key UNIQUE (name),
	CONSTRAINT providers_org_number_key UNIQUE (org_number),
	CONSTRAINT providers_pkey PRIMARY KEY (uid)
);



CREATE TABLE power_tariffs (
	valid_from timestamptz(6) NOT NULL,
	valid_to timestamptz(6) NOT NULL,
	country_code varchar(5) NOT NULL,
	last_updated timestamp(6) NOT NULL,
	provider_uid uuid NOT NULL,
	uid uuid NOT NULL,
	time_zone varchar(50) NOT NULL,
	CONSTRAINT power_tariffs_pkey PRIMARY KEY (uid),
	CONSTRAINT power_tariffs_provider_uid_key UNIQUE (provider_uid),
	CONSTRAINT fko0uef2j2oay72jdei6dlxjgoc FOREIGN KEY (provider_uid) REFERENCES providers(uid)
);


CREATE TABLE power_tariff_fees (
	samples_per_month int4 NOT NULL,
	tariff_uid uuid NOT NULL,
	uid uuid NOT NULL,
	time_unit varchar(20) NOT NULL,
	model varchar(50) NOT NULL,
	description varchar(255) NULL,
	"name" varchar(255) NOT NULL,
	building_types _text NULL,
	CONSTRAINT power_tariff_fees_pkey PRIMARY KEY (uid),
	CONSTRAINT fkt5yln46epu114rrbg9jvee8wa FOREIGN KEY (tariff_uid) REFERENCES power_tariffs(uid)
);


CREATE TABLE tariff_compositions (
	price_exc_vat numeric(38, 2) NOT NULL,
	price_inc_vat numeric(38, 2) NOT NULL,
	fuse_from varchar(10) NOT NULL,
	fuse_to varchar(10) NOT NULL,
	fee_id uuid NOT NULL,
	uid uuid NOT NULL,
	unit varchar(20) NOT NULL,
	days _text NULL,
	hints jsonb NOT NULL,
	intervals jsonb NOT NULL,
	months _int4 NULL,
	CONSTRAINT tariff_compositions_pkey PRIMARY KEY (uid),
	CONSTRAINT fkcx08ka0m8iisess3myhse1cos FOREIGN KEY (fee_id) REFERENCES power_tariff_fees(uid)
);