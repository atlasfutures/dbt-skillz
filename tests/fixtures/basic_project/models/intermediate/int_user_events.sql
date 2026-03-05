{{ config(materialized='table') }}

select
    e.event_id,
    e.user_id,
    u.email,
    e.event_name,
    count(*) over (partition by e.user_id) as event_count
from {{ ref('stg_analytics__events') }} e
left join {{ ref('stg_firestore__users') }} u using (user_id)
