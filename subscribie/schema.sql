CREATE TABLE lookups (sid text, ts timestamp , buildingnumber text, streetname text, locality text, administrative_area_level_1 text, country text, PostCode text)

CREATE TABLE person (sid text , ts timestamp, given_name text, family_name text, address_l    ine1 text, city text, postal_code text, email text, mobile text, wants text, phoneline_installed text, ph    oneline_CLI text, hasInstantPaid boolean)

CREATE TABLE mandates(sid text, ts timestamp , mandate text, customer text, flow text)

CREATE TABLE instantPayments(sid text, ts timestamp , description text, amount int)
