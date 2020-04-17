CREATE TABLE person (
    sid text , 
    ts timestamp, 
    given_name text, 
    family_name text, 
    address_line1 text,
    city text, 
    postal_code text, 
    email text, 
    mobile text, 
    wants text, 
    phoneline_installed text, 
    phoneline_CLI text, 
    hasInstantPaid boolean
);

CREATE TABLE mandates(
    sid text, 
    ts timestamp, 
    mandate text, 
    customer text, 
    flow text
);

CREATE TABLE instantPayments(
    sid text, 
    ts timestamp, 
    description text, 
    amount int
);
