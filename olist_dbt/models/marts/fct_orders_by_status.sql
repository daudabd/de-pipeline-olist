with orders as (

    select * from {{ ref('stg_orders') }}

),

status_agg as (

    select
        order_status,
        count(*) as order_count,
        avg(
            extract(epoch from (order_delivered_customer_date - order_purchase_timestamp)) / 86400.0
        ) as avg_days_purchase_to_delivery
    from orders
    group by order_status

),

total as (

    select count(*) as total_order_count from orders

)

select
    status_agg.order_status,
    status_agg.order_count,
    round(100.0 * status_agg.order_count / total.total_order_count, 2) as pct_of_orders,
    round(status_agg.avg_days_purchase_to_delivery, 2) as avg_days_purchase_to_delivery
from status_agg
cross join total
order by status_agg.order_count desc
