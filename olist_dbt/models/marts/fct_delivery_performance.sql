with orders as (

    select * from {{ ref('stg_orders') }}

),

monthly_totals as (

    -- total orders purchased in the month, regardless of delivery status;
    -- this is the true denominator behind delivered_order_count, and makes
    -- small-sample months (e.g. Sept 2016, ~4 orders) visible rather than
    -- silently inflating a rate computed on a handful of orders
    select
        date_trunc('month', order_purchase_timestamp)::date as purchase_month,
        count(*) as order_count
    from orders
    group by 1

),

delivered_orders as (

    -- only orders that have actually been delivered have a real delivery
    -- date to measure "actual" and "late" against
    select
        date_trunc('month', order_purchase_timestamp)::date as purchase_month,
        extract(epoch from (order_delivered_customer_date - order_purchase_timestamp)) / 86400.0 as actual_delivery_days,
        extract(epoch from (order_estimated_delivery_date - order_purchase_timestamp)) / 86400.0 as estimated_delivery_days,
        case when order_delivered_customer_date > order_estimated_delivery_date then 1 else 0 end as is_late
    from orders
    where order_delivered_customer_date is not null

),

delivered_agg as (

    select
        purchase_month,
        count(*) as delivered_order_count,
        avg(actual_delivery_days) as avg_actual_delivery_days,
        avg(estimated_delivery_days) as avg_estimated_delivery_days,
        sum(is_late) as late_count
    from delivered_orders
    group by purchase_month

)

select
    monthly_totals.purchase_month,
    monthly_totals.order_count,
    delivered_agg.delivered_order_count,
    round(delivered_agg.avg_actual_delivery_days, 2) as avg_actual_delivery_days,
    round(delivered_agg.avg_estimated_delivery_days, 2) as avg_estimated_delivery_days,
    round(100.0 * delivered_agg.late_count / delivered_agg.delivered_order_count, 2) as late_delivery_rate_pct
from monthly_totals
left join delivered_agg using (purchase_month)
order by monthly_totals.purchase_month
