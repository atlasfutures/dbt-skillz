{{ config(materialized='view') }}

select
    event_id,
    user_id,
    event_name
from {{ source('analytics', 'events') }}
where event_id is not null
