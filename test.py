from pip._vendor import requests
from pip._vendor.requests import post, get

print(post('http://localhost:8080/couriers',
           json=
           {
               "data": [
                   {
                       "courier_id": 1,
                       "courier_type": "foot",
                       "regions": [1, 12, 22],
                       "working_hours": ["11:35-14:05", "09:00-11:00"]
                   },
                   {
                       "courier_id": 2,
                       "courier_type": "bike",
                       "regions": [2],
                       "working_hours": ["09:00-18:00"]
                   },
                   {
                       "courier_id": 3,
                       "courier_type": "car",
                       "regions": [12, 22, 23, 33],
                       "working_hours": []
                   },

               ]
           }).json())

#
#
# print(post('http://localhost:8080/orders',
#            json=
#            {
#                "data": [
#                    {
#                        "order_id": 1,
#                        "weight": 0.23,
#                        "region": 2,
#                        "delivery_hours": ["09:00-18:00"]
#                    },
#                    {
#                        "order_id": 2,
#                        "weight": 15,
#                        "region": 2,
#                        "delivery_hours": ["09:00-18:00"]
#                    },
#                    {
#                        "order_id": 10,
#                        "weight": 0.01,
#                        "region": 2,
#                        "delivery_hours": ["09:00-12:00", "16:00-21:30"]
#                    },
#                    {
#                        "order_id": 11,
#                        "weight": 4,
#                        "region": 2,
#                        "delivery_hours": ["09:00-12:00", "16:00-21:30"]
#                    },
#                    {
#                        "order_id": 12,
#                        "weight": 4,
#                        "region": 2,
#                        "delivery_hours": ["09:00-12:00", "16:00-21:30"]
#                    },
#                    {
#                        "order_id": 6,
#                        "weight": 4,
#                        "region": 2,
#                        "delivery_hours": ["09:00-12:00", "16:00-21:30"]
#                    },
#                    {
#                        "order_id": 7,
#                        "weight": 3,
#                        "region": 2,
#                        "delivery_hours": ["09:00-12:00", "16:00-21:30"]
#                    },
#                    {
#                        "order_id": 8,
#                        "weight": 4,
#                        "region": 2,
#                        "delivery_hours": ["09:00-12:00", "16:00-21:30"]
#                    },
#                    {
#                        "order_id": 9,
#                        "weight": 4,
#                        "region": 2,
#                        "delivery_hours": ["09:00-12:00", "16:00-21:30"]
#                    }
#                ]
#            }).json())


#
# print(requests.patch('http://localhost:8080/couriers/2', json=
# {
#     'regions': [1, 2, 22]
# }).json())


# print(requests.post('http://localhost:8080/orders/assign', json=
# {
#     "courier_id": 2
# }).json())
# #
# print(requests.post('http://localhost:8080//orders/complete', json=
# {
#     "courier_id": 2,
#     "order_id": 10,
#     "complete_time": "2021-01-10T10:33:01.42Z"
# }).json())
#
# print(requests.post('http://localhost:8080//orders/complete', json=
# {
#     "courier_id": 2,
#     "order_id": 11,
#     "complete_time": "2021-01-10T10:33:01.42Z"
# }).json())
#
# print(requests.post('http://localhost:8080//orders/complete', json=
# {
#     "courier_id": 2,
#     "order_id": 12,
#     "complete_time": "2021-01-10T10:33:01.42Z"
# }).json())
#
# print(requests.post('http://localhost:8080//orders/complete', json=
# {
#     "courier_id": 2,
#     "order_id": 9,
#     "complete_time": "2021-01-10T10:33:01.42Z"
# }).json())

# print(get('http://localhost:8080/couriers/2').json())
