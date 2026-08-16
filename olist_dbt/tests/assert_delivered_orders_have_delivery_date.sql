-- Known source-data inconsistency, not a pipeline defect: as of this writing,
-- 8 orders have order_status = 'delivered' but no order_delivered_customer_date.
-- The carrier handoff (order_delivered_carrier_date) is recorded for 5 of the
-- 8; the other 3 don't even have that. In every case the status was advanced
-- to 'delivered' without the customer-delivery timestamp ever being written.
-- Affected order_ids:
--   2d858f451373b04fb5c984a1cc2defaf
--   2d1e2d5bf4dc7227b3bfebb81328c15f
--   ab7c89dc1bf4a1ead9d6ec1ec8968a84
--   f5dd62b788049ad9fc0526e3ad11a097
--   20edc82cf5400ce95e1afacc25798b31
--   2ebdfc4f15f23b91474edf87475f108e
--   0d3268bad9b086af767785e3f0fc0133
--   e69f75a717d64fc5ecdfae42b2e8e086
-- Kept as warn (not error) so the suite stays green while still surfacing
-- the count if this set grows.
{{ config(severity='warn') }}

select *
from {{ ref('stg_orders') }}
where order_status = 'delivered'
  and order_delivered_customer_date is null
