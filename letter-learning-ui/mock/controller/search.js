const List = [
    {
        url: 'https://www.bing.com/search?q=vue+admin+plus%e5%ae%98%e7%bd%91&qs=HS&pq=vue+admin+plus&sk=HS1&sc=10-14&cvid=B01F4326D6724F76B568CBF127648BB8&FORM=QBRE&sp=2&lq=0&rdr=1&rdrig=7414F5AB9CF241C78B8CC476818B3569',
        value: '官网',
    },
]

module.exports = [
    {
        url: '/search/getList',
        type: 'get',
        response: () => {
            return {
                code: 200,
                msg: 'success',
                data: { list: List },
            }
        },
    },
]
