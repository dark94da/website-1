from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404

from .models import Deal, UsedCar, Image, UserPro

import datetime


def getCarpool(deal):
    carpool = deal.carpool
    res={
        "出发日期" : carpool.date,
        '出发时间' : carpool.time,
        '出发地点' : carpool.depart_place,
        '目的地' : carpool.destination,
        '最大乘客人数' : carpool.passenger_num,
        '人均价格' : carpool.price,
        '车辆类型' : carpool.car_type,
    }
    if carpool.note:
        res.update({'补充说明' : carpool.note})
    return res

def getUsedCar(deal):
    car=UsedCar.objects.get(deal=deal)
    res={
        "年份": car.year,
        "品牌": car.car_brand,
        "型号": car.car_model,
        "里程数" : car.mileage,
        "售价" : car.price,
    }
    if car.note:
        res.update({"补充说明" : car.note})
    return res

def getUsedItem(deal):
    item = deal.useditem
    res = {
        "商品类型": item.item_type,
        '商品描述': item.item_name,
        '新旧情况': item.condition,
        '价格': item.price,
    }
    if item.note:
        res.update({'补充说明': item.note})
    return res

def getSublease(deal):
    lease = deal.sublease
    res = {
        "小区名称": lease.community,
        "卧室数量": lease.bedroom_num,
        "浴室数量": lease.bathroom_num,
        "月租": lease.rent,
        "开始日期": lease.start_date,
        '结束日期' : lease.end_date,
    }
    if lease.renewal==1:
        res.update({'可否续租' : '是'})
    else:
        res.update({'可否续租' : '否'})
    if lease.note:
        res.update({"补充说明": lease.note})
    return res

def getHouseRent(deal):
    houserent = deal.houserent
    res = {
        '小区名称' : houserent.community,
        '卧室数量' : houserent.bedroom_num,
        '浴室数量' : houserent.bathroom_num,
        '月租' : houserent.rent,
        '开始日期' : houserent.start_date,
        '合租时间' : houserent.duration,
    }
    if houserent.roommate_gender=='both':
        res.update({'室友性别要求' : '男女均可'})
    elif houserent.roommate_gender=='female':
        res.update({'室友性别要求' : '仅女生'})
    else:
        res.update({'室友性别要求' : '仅男生'})
    if houserent.note:
        res.update({"补充说明": houserent.note})
    return res

def getMergeOrder(deal):
    order = deal.mergeorder
    res = {
        '活动网址' : order.website,
        '商品类型' : order.order_type,
        '截止日期' : order.duedate,
    }
    if order.note:
        res.update({"补充说明": order.note})
    return res

def getContact(deal):
    user=deal.posted_user
    res={}
    userpro=UserPro.objects.get(user=user)
    if "1" in deal.contact_type:
        res.update({'email': user.username})
    if "2" in deal.contact_type:
        res.update({'phone' : userpro.phone})
    if "3" in deal.contact_type:
        res.update({'wechat': userpro.wechat})
    return res

def getDealDetail(request, deal_id):
    deal=get_object_or_404(Deal, id=deal_id)

    is_overdue = True if deal.expire_time<datetime.datetime.now().date() else False
    is_saved = True if deal.saved_users.filter(id=request.user.id) else False
    is_author = True if request.user == deal.posted_user else False

    if (request.user.is_authenticated() and not is_saved and is_overdue and not is_author) or (not request.user.is_authenticated() and is_overdue):
        return render(request, 'webapps/error.html')

    config = {'is_overdue' : is_overdue, 'is_saved' : is_saved, 'is_author' : is_author, 'deal_id': deal.id}
    config.update(getContact(deal))

    d = {
        'carpool': getCarpool,
        'usedcar': getUsedCar,
        'useditem' : getUsedItem,
        'sublease' : getSublease,
        'mergeorder' : getMergeOrder,
        'houserent' : getHouseRent,
    }
    text = {"发布时间": deal.create_time}
    text.update(d[deal.type](deal))
    images=Image.objects.filter(deal=deal)

    return render(request, 'webapps/detail.html', {'text': text, 'images': images, 'config' : config })

@login_required
def saveDeal(request):
    deal_id=request.GET['deal_id']
    deal=Deal.objects.get(id=deal_id)
    deal.saved_users.add(request.user)
    deal.save()
    contact=getContact(deal)
    return JsonResponse({'status' : 'success', 'contact' :contact})

@login_required
def unsaveDeal(request):
    deal_id=request.GET['deal_id']
    deal=Deal.objects.get(id=deal_id)
    deal.saved_users.remove(request.user)
    deal.save()
    return JsonResponse({'status': 'success'})

@login_required
def loadMoreDeal(request):
    res={}
    type=request.GET['type']
    start=int(request.GET['end'])
    deals = Deal.objects.filter(posted_user=request.user).order_by('create_time')
    if type:
        deals = deals.filter(type=type)
    deals=deals[start:start+10]
    res['has_next']=True if deals.count()==10 else False
    res['end']=start+10
    res['type']=type
    records = []
    for deal in deals:
        record = {'id': deal.id,
                  'title': deal.__str__(),
                  'type': deal.type,
                  'create_time': deal.create_time,
                  'expire_time': deal.expire_time,
                  'hot_index': deal.hot_index,
                  }
        records.append(record)
    res['records']=records
    res['status']='success'
    return JsonResponse(res)

