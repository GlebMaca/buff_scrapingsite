from django.shortcuts import get_object_or_404, redirect ,render
from django.http import HttpResponse,Http404,HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.http import JsonResponse

from .models import Question,Choice


import json
import os
import re
import time
import threading

import requests

from decimal import *
from http.cookies import SimpleCookie

from requests.cookies import cookiejar_from_dict
from termcolor import cprint, colored



dir_path = os.path.dirname(os.path.realpath(__file__))
with open(dir_path + '/config.json') as fp:
    config = json.load(fp)


base_url = 'https://buff.163.com'
buff_api = 'https://buff.163.com/api/market/goods'
buff_good_api='https://buff.163.com/api/market/goods/info'
buff_wait_api='https://buff.163.com/api/market/buy_order/wait_supply'
buff_order_api = 'https://buff.163.com/api/market/goods/buy_order'
buff_create_order='https://buff.163.com/api/market/buy_order/create'
buff_cancel_order='https://buff.163.com/api/market/buy_order/cancel'


item_nameid_pattern = re.compile(r'Market_LoadOrderSpread\(\s*(\d+)\s*\)')
wanted_cnt_pattern = re.compile(r'<span\s*class="market_commodity_orders_header_promote">(\d+)</span>')
csrf_pattern = re.compile(r'name="csrf_token"\s*content="(.+?)"')

buff_opener = requests.session()
for key, value in config['buff']['requests_kwargs'].items():
    setattr(buff_opener, key, value)



s = requests.session()
simple_cookie = SimpleCookie()
simple_cookie.load(config['buff']['requests_kwargs']['headers']['cookie'])
buff_cookies = {}
for key, morsel in simple_cookie.items():
    buff_cookies[key] = morsel.value
buff_opener.cookies = cookiejar_from_dict(buff_cookies)


def index(request):
    
    total_page = buff_opener.get(buff_wait_api, params={
            'page_num': 1,
            'game': config['main']['game']
        }).json()['data']['total_page']
    
    
    good_buy_order_items=[]
    lower_buy_order_items=[]
    pro_buy_order_items=[]
    for each_page in range(1, total_page + 1):
        res = buff_opener.get(buff_wait_api, params={
            'page_num': each_page,
            'game': config['main']['game']
        }).json()
        
        if res['code'] != 'OK':
            print(res, flush=True)
            exit(1)

        items = res['data']['items']    
        
        for item in items:
            
            
            goods_id=item['goods_id']
            good_inf=buff_opener.get(buff_good_api, params={                  
                'game': config['main']['game'],
                'goods_id':goods_id
            }).json()['data']
            
            sell_min_price=good_inf['sell_min_price']
            title=good_inf['share_data']['title']

            good_url=base_url+"/goods/"+str(goods_id)
           
            good_detail=buff_opener.get(good_url).text
            # print(good_detail)
            
            ref_pattern = re.compile(r'data-price="(\w+.\w+)" data-type="big"')
            reference_price=ref_pattern.findall(good_detail)[0]
            # reference_price=good_inf['sell_reference_price']
            
            reference_price=float('%.2f' % float(reference_price))
            
            good_inf=buff_opener.get(buff_good_api, params={                  
                'game': config['main']['game'],
                'goods_id':goods_id
            }).json()['data']




            
            res_order = buff_opener.get(buff_order_api, params={
                'page_num': each_page,
                'game': config['main']['game'],
                'goods_id':goods_id
            }).json()
            
            if res_order['code'] != 'OK':
                print(res_order, flush=True)
                exit(1)

            order_items = res_order['data']['items']
            
            goods_id=item['goods_id']
            price=item['price']
            buy_max_price=item['buy_max_price']
            num=item['num']
            pay_method=item['pay_method']
            order_id=item['id']
            allow_tradable_cooldown=item['allow_tradable_cooldown']
            specific=item['specific']
            change_price=float(buy_max_price)+0.1
            change_price=float('%.1f' % (change_price))
            icon_url=item['icon_url']
            total=float('%.2f' % (int(num)*float(price)))
            print(total)
            if len(order_items)==1:
                
                good_buy_order_items.append({'title':title,
                                    'goods_id':goods_id,
                                    'pay_method':pay_method,
                                    'price':price,
                                    'second_price':0,
                                    'icon_url':icon_url,
                                    'num':num,
                                    'allow_tradable_cooldown':0,
                                    'specific':specific,
                                    'order_id':order_id,
                                    'total':total,
                                    'sell_min_price':sell_min_price
                                    })
                continue
            first_id=order_items[0]['id']
            first_price=order_items[0]['price']
            
            second_id=order_items[1]['id']
            second_price=order_items[1]['price'] 

            if reference_price< 1 :
                price_unit=0.01
                cut_str='%.2f'
            elif reference_price< 50 :
                price_unit=0.1
                cut_str='%.1f'
            elif reference_price<1000:
                price_unit=1
                cut_str='%.f'
            else:
                price_unit=10
                cut_str='%.f'
            
            if first_id==order_id:
               
                x1=float(first_price)
                x2=float(second_price)
                delta=float(cut_str % (x1-x2))
              
                if delta<=price_unit:
                    print("yes")
                    good_buy_order_items.append({'title':title,
                                'goods_id':goods_id,
                                'pay_method':pay_method,
                                'price':price,
                                'second_price':second_price,
                                'icon_url':icon_url,
                                'num':num,
                                'allow_tradable_cooldown':0,
                                'specific':specific,
                                'order_id':order_id,
                                'total':total,
                                'sell_min_price':sell_min_price
                                })

                    continue
                else:
                    lower_buy_order_items.append({'title':title,
                                    'goods_id':goods_id,
                                    'pay_method':pay_method,
                                    'price':price,
                                    'second_price':second_price,
                                    'icon_url':icon_url,
                                    'num':num,
                                    'allow_tradable_cooldown':0,
                                    'specific':specific,
                                    'order_id':order_id,
                                    'total':total,
                                    'sell_min_price':sell_min_price
                                    })  

                    continue
            else:
                pro_buy_order_items.append({'title':title,
                                    'goods_id':goods_id,
                                    'pay_method':pay_method,
                                    'price':price,
                                    'second_price':second_price,
                                    'icon_url':icon_url,
                                    'num':num,
                                    'allow_tradable_cooldown':0,
                                    'specific':specific,
                                    'order_id':order_id,
                                    'total':total,
                                    'sell_min_price':sell_min_price
                                    })     
            
            
           

    


 

    latest_question_list=Question.objects.order_by('-pub_state')[:5]
    template = loader.get_template('polls/index.html')
    context={'latest_question_list':latest_question_list}
    orderlist={'good_orderlist':good_buy_order_items,
                'lower_orderlist':lower_buy_order_items,
                'pro_orderlist':pro_buy_order_items}
  
    # return HttpResponse(template.render(context,request))
    # return JsonResponse({'foo':'bar'})
    #  return render(request,'polls/index.html',context)
    return render(request,'tables.html',orderlist)
def delete(request,order_id):
   
    csrf_token = csrf_pattern.findall(
                    buff_opener.get(base_url).text
                )

    if not csrf_token:
        raise RuntimeError
  

    buff_opener.headers['X-CSRFToken'] = csrf_token[0]
    buff_opener.headers['Referer'] = base_url
 
    result=buff_opener.post(buff_cancel_order,json={
                        'game': config['main']['game'],
                        'buy_orders': [order_id]
                    }).json()
    return JsonResponse(result)
def edit(request,edit_order_id,edit_goods_id):
    print(edit_goods_id)
    print(edit_order_id)
    
    total_page = buff_opener.get(buff_wait_api, params={
        'page_num': 1,
        'game': config['main']['game']
    }).json()['data']['total_page']
    
    cancel_orders=[]
    create_orders=[]
    for each_page in range(1, total_page + 1):
        res = buff_opener.get(buff_wait_api, params={
            'page_num': each_page,
            'game': config['main']['game']
        }).json()
        
        if res['code'] != 'OK':
            print(res, flush=True)
            exit(1)

        items = res['data']['items']
        
        for item in items:          
            
            goods_id=item['goods_id']
            print(goods_id)
            if str(goods_id)!=str(edit_goods_id):
                continue
            print("okk")
            good_url=base_url+"/goods/"+str(goods_id)
           
            good_detail=buff_opener.get(good_url).text
            # print(good_detail)
            
            ref_pattern = re.compile(r'data-price="(\w+.\w+)" data-type="big"')
            reference_price=ref_pattern.findall(good_detail)[0]
            # reference_price=good_inf['sell_reference_price']
            
            reference_price=float('%.2f' % float(reference_price))
           
            good_inf=buff_opener.get(buff_good_api, params={                  
                'game': config['main']['game'],
                'goods_id':goods_id
            }).json()['data']
            
            sell_min_price=good_inf['sell_min_price']
            
            res_order = buff_opener.get(buff_order_api, params={
                'page_num': 1,
                'game': config['main']['game'],
                'goods_id':goods_id
            }).json()
            
            if res_order['code'] != 'OK':
                print(res_order, flush=True)
                exit(1)

            order_items = res_order['data']['items']
            
            if len(order_items)==1:
                continue
            first_id=order_items[0]['id']
            first_price=order_items[0]['price']
            
            second_id=order_items[1]['id']
            second_price=order_items[1]['price']
            cut_str='%.2f'
            if reference_price< 1 :
                price_unit=0.01
                cut_str='%.2f'
            elif reference_price< 50 :
                price_unit=0.1
                cut_str='%.1f'
            elif reference_price<1000:
                price_unit=1
                cut_str='%.f'
            else:
                price_unit=10
                cut_str='%.f'


                            

            goods_id=item['goods_id']
            price=item['price']
            buy_max_price=item['buy_max_price']
            num=item['num']
            pay_method=item['pay_method']
            order_id=item['id']
            allow_tradable_cooldown=item['allow_tradable_cooldown']
            specific=item['specific']
            change_price=float(buy_max_price)+price_unit
            change_price=float(cut_str % (change_price))
            
            if first_id==order_id:
                change_price=float(second_price)+price_unit
                change_price=float(cut_str % (change_price))
                # print(first_price)
                # print(second_price)
                x1=float(first_price)
                x2=float(second_price)
                delta=float(cut_str % (x1-x2))
                print(x1)
                print(x2)
                print(delta)
                if delta<=price_unit:
                    print("yes")

                    continue  
                print(x1)
                print(x2)
                print(delta)
                print("no")          
            
            cancel_orders.append(order_id)
            create_orders.append({'goods_id':goods_id,
                                    'pay_method':pay_method,
                                    'change_price':change_price,
                                    'num':num,
                                    'allow_tradable_cooldown':0,
                                    'specific':specific,
                                    'order_id':order_id
                                    })


    result={"error":"error"}
    if len(create_orders)>0:
        
     
        
        for create_order in create_orders:
            csrf_token = csrf_pattern.findall(
                buff_opener.get(base_url).text
            )

            if not csrf_token:
                raise RuntimeError

            buff_opener.headers['X-CSRFToken'] = csrf_token[0]
            buff_opener.headers['Referer'] = base_url


            print('start')
            buff_opener.post(buff_cancel_order,json={
                    'game': config['main']['game'],
                    'buy_orders': [create_order['order_id']]
                })
            print('cancel')
            print(create_order['goods_id'])
            
            csrf_token = csrf_pattern.findall(
                buff_opener.get(base_url).text
            )

            if not csrf_token:
                raise RuntimeError
            print(csrf_token)
            buff_opener.headers['X-CSRFToken'] = csrf_token[0]
            # buff_opener.headers['Referer'] = base_url
            game=config['main']['game']
            goods_id=create_order['goods_id']
            num=create_order['num']
            price= create_order['change_price']
            create_data={
                    'game': game,
                    'goods_id': goods_id,
                    'price': price,
                    'num': num,
                    'pay_method': 3,                      
                    'specific':  [],
                    'allow_tradable_cooldown': 0

                }
            print(create_data)
            time.sleep(20)
            create_result=buff_opener.post(buff_create_order,json=create_data)
            
            print(create_result.json()['code'])
            if(create_result.json()['code']=='BuyOrder Create Cooling Down'):                       
                
                csrf_pattern_header =  re.compile(r'csrf_token=(\w.+);')
                csrf_token = csrf_pattern.findall( buff_opener.get(base_url).text    )

                if not csrf_token:
                    raise RuntimeError
                print(csrf_token)
                time.sleep(20)
                buff_opener.headers['X-CSRFToken'] = csrf_token[0]
                # buff_opener.headers['Referer'] = base_url
                create_result=buff_opener.post(buff_create_order,json=create_data)
                result=create_result.json()
                print(result)
                
    
    return JsonResponse(result)
 



            
            
    
  
def detail(request,question_id):
    # try:
    #      question = Question.objects.get(pk=question_id)
    # except Question.DoesNotExist:
    #      raise Http404("Question does not exist")
    # return render(request,'polls/detail.html',{'question':question})
    question=get_object_or_404(Question,pk=question_id)
    return render(request,'polls/detail.html',{'question':question})

    
    # return HttpResponse("You're looking at question%s" % question_id)

def results(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, 'polls/results.html', {'question': question})
# def results(request,question_id):
#     question=get_object_or_404(Question,question_id)
#     return render(request,'polls/results.html',{'question':question})
    # response ="You're looking at the results of questions %s"
    # return HttpResponse(response % question_id)
def vote(request,question_id):
    question=get_object_or_404(Question, pk=question_id)
    try:
        selected_choice=question.choice_set.get(pk=request.POST['choice'])
    except(KeyError,Choice.DoesNotExist):
        return render(request,'polls/detail.html',{
            'question':question,
            'error_message':"You didn't select a choice."
            
        })
    else:
        selected_choice.votes+=1
        selected_choice.save()
        # return HttpResponseRedirect(reverse('poll:results',args=(question.id)))
        return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))
    
    # return HttpResponse("You're voting on question %s." % question_id)
# Create your views here.
class IndexView(generic.ListView):
    template_name='polls/index.html'
    context_object_name="latest_question_list"
    def get_queryset(self):      
            return Question.objects.filter(pub_state__lte=timezone.now()).order_by('-pub_state')[:5]
    # def get_queryset(self):
    #     # return Question.objects.order_by('-pub_state')[:5]
    #     return Question.objects.filter(pub_state__lte=timezone.now()).order_by('-pub_state')[:5]
class DetailView(generic.DetailView):
    model=Question
    template_name="polls/detail.html"
    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())
class ResultsView(generic.DetailView):
    model=Question
    template_name='polls/results.html'