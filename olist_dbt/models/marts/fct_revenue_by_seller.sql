with order_items as (

    select * from {{ ref('stg_order_items') }}

),

seller_agg as (

    select
        seller_id,
        sum(price) as total_revenue,
        count(distinct order_id) as order_count
    from order_items
    group by seller_id

)

select
    seller_id,
    total_revenue,
    order_count,
    round(total_revenue / nullif(order_count, 0), 2) as avg_order_value,
    rank() over (order by total_revenue desc) as revenue_rank
from seller_agg
order by total_revenue desc
