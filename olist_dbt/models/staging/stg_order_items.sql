with source as (

    select * from {{ source('olist_raw', 'order_items') }}

)

select
    order_id::text as order_id,
    order_item_id::integer as order_item_id,
    product_id::text as product_id,
    seller_id::text as seller_id,
    shipping_limit_date::timestamp as shipping_limit_date,
    price::numeric as price,
    freight_value::numeric as freight_value
from source
