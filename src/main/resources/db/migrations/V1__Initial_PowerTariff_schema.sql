-- Initial PowerTariff schema
-- Original Alembic revision: 9824b55b6d3b

-- Create grid_operators table
CREATE TABLE grid_operators (
    uid UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    ediel INTEGER NOT NULL UNIQUE
);

-- Create indexes for grid_operators
CREATE INDEX ix_grid_operators_name ON grid_operators(name);
CREATE INDEX ix_grid_operators_ediel ON grid_operators(ediel);

-- Create metering_grid_areas table
CREATE TABLE metering_grid_areas (
    code VARCHAR(5) PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    country_code VARCHAR(2) NOT NULL DEFAULT 'SE',
    metering_business_area VARCHAR(5) NOT NULL,
    grid_operator_uid UUID NOT NULL
);

-- Add foreign key constraint
ALTER TABLE metering_grid_areas
    ADD CONSTRAINT fk_metering_grid_areas_grid_operator_uid
    FOREIGN KEY (grid_operator_uid)
    REFERENCES grid_operators(uid);

-- Create index for foreign key
CREATE INDEX ix_metering_grid_areas_grid_operator_uid
    ON metering_grid_areas(grid_operator_uid);

-- Create power_tariffs table
CREATE TABLE power_tariffs (
    uid UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    model VARCHAR(50) NOT NULL,
    description TEXT,
    samples_per_month INTEGER NOT NULL,
    time_unit VARCHAR(20) NOT NULL,
    building_type VARCHAR(50) NOT NULL DEFAULT 'All',
    last_updated TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    valid_from TIMESTAMP WITH TIME ZONE,
    valid_to TIMESTAMP WITH TIME ZONE,
    voltage VARCHAR(10) NOT NULL,
    compositions JSONB NOT NULL
);

-- Create junction table for many-to-many relationship
CREATE TABLE metering_grid_area_x_power_tariff (
    uid UUID PRIMARY KEY,
    mga_code VARCHAR(5) NOT NULL,
    tariff_uid UUID NOT NULL
);

-- Add foreign key constraints for junction table
ALTER TABLE metering_grid_area_x_power_tariff
    ADD CONSTRAINT fk_mgas_x_tariffs_mga_code
    FOREIGN KEY (mga_code)
    REFERENCES metering_grid_areas(code);

ALTER TABLE metering_grid_area_x_power_tariff
    ADD CONSTRAINT fk_mgas_x_tariffs_tariff_uid
    FOREIGN KEY (tariff_uid)
    REFERENCES power_tariffs(uid);

-- Create indexes for the junction table
CREATE INDEX ix_metering_grid_area_x_power_tariff_mga_code
    ON metering_grid_area_x_power_tariff(mga_code);

CREATE INDEX ix_metering_grid_area_x_power_tariff_tariff_uid
    ON metering_grid_area_x_power_tariff(tariff_uid);

-- Create composite unique index for better query performance
CREATE UNIQUE INDEX ix_metering_grid_area_x_power_tariff_mga_tariff
    ON metering_grid_area_x_power_tariff(mga_code, tariff_uid);
