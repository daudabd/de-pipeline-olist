-- fails if the estimated delivery date is before the order was even purchased
select *
from {{ ref('stg_orders') }}
where order_estimated_delivery_date < order_purchase_timestamp
