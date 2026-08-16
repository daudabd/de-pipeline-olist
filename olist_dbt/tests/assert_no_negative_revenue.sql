-- fails if any seller has negative total revenue
select *
from {{ ref('fct_revenue_by_seller') }}
where total_revenue < 0
