select
        l_shipdate,
        l_commitdate,
        l_receiptdate,
        count(*) as count_order
from
	lineitem
group by
	l_shipdate,
        l_commitdate,
        l_receiptdate
order by
	l_shipdate,
	count_order;
