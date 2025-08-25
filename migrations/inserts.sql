-- 1. Insert provider
INSERT INTO providers
    (uid, name, org_number, ediel, active)
VALUES
    ('018e9660-8b8f-7416-b09a-528fc4c3e9a9', 'Tekniska verken Linköping Nät AB', '556483-4926', 11900, TRUE);

-- 2. Insert power tariff
INSERT INTO power_tariffs
    (uid, provider_uid, country_code, time_zone, last_updated, valid_from, valid_to)
VALUES
    ('018e9660-8b93-74e1-bf2c-e7bd3bda5ddb', '018e9660-8b8f-7416-b09a-528fc4c3e9a9', 'SE', 'Europe/Stockholm', NOW(), '2025-01-01', '2025-12-31');

-- 3. Insert power tariff fees
INSERT INTO power_tariff_fees
    (uid, tariff_uid, name, model, description, samples_per_month, time_unit, building_types)
VALUES
    ('018e9660-8b97-74c2-98b9-354f3dc31780', '018e9660-8b93-74e1-bf2c-e7bd3bda5ddb', 'Default Standard fee', 'avgMonthlyPeaks', 'Average of the 5 monthly highest power peaks (kW/h)', 5, 'hourly', ARRAY['detached_house','terraced_house','summer_house','apartments']),
    ('018e9660-8b9b-7436-bfa2-4e8ac3db4904', '018e9660-8b93-74e1-bf2c-e7bd3bda5ddb', 'Alternative fee', 'avgMonthlyPeaks', 'Average of the 2 nightly and daily highest power peaks (kW/h)', 2, 'hourly', ARRAY['detached_house','terraced_house','summer_house','apartments']);

-- 4. Insert tariff compositions
INSERT INTO tariff_compositions
    (uid, fee_id, months, days, fuse_from, fuse_to, hints, unit, price_exc_vat, price_inc_vat, intervals)
VALUES
    -- Linköping Summer (Default)
    ('018e9660-8b9f-747a-9e60-fc7e6efcae9e', '018e9660-8b97-74c2-98b9-354f3dc31780', ARRAY[4,5,6,7,8,9,10], ARRAY['M','T','W','T','F','S','S'], '16A', '63A',
        '[{"type":"geolocation","value":"linköping"},{"type":"season","value":"summer"}]', 'kr/kw', 16.5, 22,
        '[{"from":"00:00","to":"23:59","multiplier":1}]'::json),
    -- Linköping Winter (Default)
    ('018e9660-8ba2-742e-b289-9603c45391e5', '018e9660-8b97-74c2-98b9-354f3dc31780', ARRAY[1,2,3,11,12], ARRAY['M','T','W','T','F','S','S'], '16A', '63A',
        '[{"type":"geolocation","value":"linköping"},{"type":"season","value":"winter"}]', 'kr/kw', 32.25, 43,
        '[{"from":"00:00","to":"23:59","multiplier":1}]'::json),
    -- Linköping Summer Day (Alternative)
    ('018e9660-8ba6-74fb-9303-4bb84d04e3f7', '018e9660-8b9b-7436-bfa2-4e8ac3db4904', ARRAY[4,5,6,7,8,9,10], ARRAY['M','T','W','T','F','S','S'], '16A', '63A',
        '[{"type":"geolocation","value":"linköping"},{"type":"season","value":"summer"},{"type":"timeOfDay","value":"day"}]', 'kr/kw', 16.5, 22,
        '[{"from":"06:00","to":"23:00","multiplier":1}]'::json),
    -- Linköping Summer Night (Alternative)
    ('018e9660-8ba9-7448-bd3b-3c7b78877aad', '018e9660-8b9b-7436-bfa2-4e8ac3db4904', ARRAY[4,5,6,7,8,9,10], ARRAY['M','T','W','T','F','S','S'], '16A', '63A',
        '[{"type":"geolocation","value":"linköping"},{"type":"season","value":"summer"},{"type":"timeOfDay","value":"night"}]', 'kr/kw', 6, 8,
        '[{"from":"23:01","to":"05:59","multiplier":1}]'::json),
    -- Linköping Winter Day (Alternative)
    ('018e9660-8bad-74bb-94f5-2dbe76fddb89', '018e9660-8b9b-7436-bfa2-4e8ac3db4904', ARRAY[1,2,3,11,12], ARRAY['M','T','W','T','F','S','S'], '16A', '63A',
        '[{"type":"geolocation","value":"linköping"},{"type":"season","value":"winter"},{"type":"timeOfDay","value":"day"}]', 'kr/kw', 32.25, 43,
        '[{"from":"06:00","to":"23:00","multiplier":1}]'::json),
    -- Linköping Winter Night (Alternative)
    ('018e9660-8bb0-74e8-b85b-f1407e79df51', '018e9660-8b9b-7436-bfa2-4e8ac3db4904', ARRAY[1,2,3,11,12], ARRAY['M','T','W','T','F','S','S'], '16A', '63A',
        '[{"type":"geolocation","value":"linköping"},{"type":"season","value":"winter"},{"type":"timeOfDay","value":"night"}]', 'kr/kw', 9, 12,
        '[{"from":"23:01","to":"05:59","multiplier":1}]'::json);