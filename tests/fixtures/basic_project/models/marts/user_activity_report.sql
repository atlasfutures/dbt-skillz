{{ config(materialized='table') }}

select
    user_id,
    email,
    count(distinct event_id) as total_events,
    max(event_id) as last_activity_date
from {{ ref('int_user_events') }}
group by 1, 2
