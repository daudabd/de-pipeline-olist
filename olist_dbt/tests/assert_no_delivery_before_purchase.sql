-- fails if any order has a delivery date earlier than its purchase date
select *
from {{ ref('stg_orders') }}
where order_delivered_customer_date < order_purchase_timestamp
