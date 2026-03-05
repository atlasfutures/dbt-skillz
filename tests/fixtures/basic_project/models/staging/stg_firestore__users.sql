{{ config(materialized='view') }}

select
    user_id,
    email,
    created_at
from {{ source('firestore', 'users') }}
where user_id is not null
