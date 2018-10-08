from django.db import models
import time
import logging

logger = logging.getLogger('django')


# Create your models here.


class InfoManager(models.Manager):

    def save_userinfo(self, taobao_total_data):
        # 保存个人账户信息
        user_id = taobao_total_data["user_id"]
        login_name = taobao_total_data["tb_user"]["login_name"]
        vip_level = taobao_total_data["tb_user"]["vip_level"]
        score = taobao_total_data["tb_user"]["score"]
        rate_summary = taobao_total_data["tb_user"]["rate_summary"]
        email = taobao_total_data["tb_user"]["email"]
        binding_phone = taobao_total_data["tb_user"]["binding_phone"]
        authentication = taobao_total_data["tb_user"]["authentication"]
        name = taobao_total_data["tb_user"]["name"]
        address = taobao_total_data["tb_user"]["address"]
        tianmao_grade = taobao_total_data["tb_user"]["tianmao_grade"]
        userinfo = UserInfo(user_id=user_id,
                            login_name=login_name,
                            vip_level=vip_level,
                            score=score,
                            rate_summary=rate_summary,
                            email=email,
                            binding_phone=binding_phone,
                            authentication=authentication,
                            name=name,
                            address=address,
                            tianmao_grade=tianmao_grade)
        try:
            userinfo.save()
        except Exception as e:
            logger.error(e)
        return userinfo

    def save_orderinfo(self, taobao_total_data):
        # 保存订单信息
        num = 0
        while num < len(taobao_total_data["tb_order"]["order_list"]):
            user_id = taobao_total_data["user_id"]
            order_id = taobao_total_data["tb_order"]["order_list"][num]["order_id"]
            status = taobao_total_data["tb_order"]["order_list"][num]["status"]
            actual_yuan = taobao_total_data["tb_order"]["order_list"][num]["actual_yuan"]
            phone_order = taobao_total_data["tb_order"]["order_list"][num]["phone_order"]
            transaction_time = taobao_total_data["tb_order"]["order_list"][num]["transaction_time"]
            payment_time = taobao_total_data["tb_order"]["order_list"][num]["payment_time"]
            confirmation_time = taobao_total_data["tb_order"]["order_list"][num]["confirmation_time"]
            receiver_name = taobao_total_data["tb_order"]["order_list"][num]["receiver_name"]
            receiver_telephone = taobao_total_data["tb_order"]["order_list"][num]["receiver_phone"]
            receiver_address = taobao_total_data["tb_order"]["order_list"][num]["receiver_address"]
            orderinfo = OrderInfo(user_id=user_id,
                                  order_id=order_id,
                                  status=status,
                                  actual_yuan=actual_yuan,
                                  phone_order=phone_order,
                                  transaction_time=transaction_time,
                                  payment_time=payment_time,
                                  confirmation_time=confirmation_time,
                                  receiver_name=receiver_name,
                                  receiver_telephone=receiver_telephone,
                                  receiver_address=receiver_address)
            try:
                orderinfo.save()
            except Exception as e:
                logger.error(e)
            num += 1

    def save_productinfo(self, taobao_total_data):
        # 保存商品信息
        user_id = taobao_total_data["user_id"]
        num1 = 0
        while num1 < len(taobao_total_data["tb_order"]["order_list"]):
            order_id = taobao_total_data["tb_order"]["order_list"][num1]["order_id"]
            product_obj = taobao_total_data["tb_order"]["order_list"][num1]["products"]
            if not product_obj:
                num1 += 1
                continue
            num2 = 0
            while num2 < len(taobao_total_data["tb_order"]["order_list"][num1]["products"]):
                product_quantity = taobao_total_data["tb_order"]["order_list"][num1]["products"][num2][
                    "product_quantity"]
                product_name = taobao_total_data["tb_order"]["order_list"][num1]["products"][num2]["product_name"]
                product_price = taobao_total_data["tb_order"]["order_list"][num1]["products"][num2]["product_price"]
                productinfo = ProductInfo(user_id=user_id,
                                          order_id=order_id,
                                          product_name=product_name,
                                          product_price=product_price,
                                          product_quantity=product_quantity)
                try:
                    productinfo.save()
                except Exception as e:
                    logger.error(e)
                num2 += 1
            num1 += 1

    def save_deliveraddrsinfo(self, taobao_total_data):
        # 保存收货地址信息
        user_id = taobao_total_data["user_id"]
        num = 0
        while num < len(taobao_total_data["tb_deliver_addrs"]):
            receiver_name = taobao_total_data["tb_deliver_addrs"][num]["receiver_name"]
            area = taobao_total_data["tb_deliver_addrs"][num]["area"]
            address = taobao_total_data["tb_deliver_addrs"][num]["address"]
            zip_code = taobao_total_data["tb_deliver_addrs"][num]["zip_code"]
            phone = taobao_total_data["tb_deliver_addrs"][num]["phone"]
            is_default_address = taobao_total_data["tb_deliver_addrs"][num]["is_default_address"]
            deliveraddrsinfo = DeliverAddrsInfo(user_id=user_id,
                                                receiver_name=receiver_name,
                                                area=area,
                                                address=address,
                                                zip_code=zip_code,
                                                phone=phone,
                                                is_default_address=is_default_address)
            try:
                deliveraddrsinfo.save()
            except Exception as e:
                logger.error(e)
            num += 1

    def save_zhifubaoinfo(self, taobao_total_data):
        # 保存支付宝账户信息
        user_id = taobao_total_data["user_id"]
        zhifubao_account = taobao_total_data["tb_zhifubao_binding"]["zhifubao_account"]
        balance = taobao_total_data["tb_zhifubao_binding"]["balance"]
        total_quotient = taobao_total_data["tb_zhifubao_binding"]["total_quotient"]
        total_profit = taobao_total_data["tb_zhifubao_binding"]["total_profit"]
        huabei_credit_amount = taobao_total_data["tb_zhifubao_binding"]["huabei_credit_amount"]
        huabei_total_credit_amount = taobao_total_data["tb_zhifubao_binding"]["huabei_total_credit_amount"]
        binding_phone = taobao_total_data["tb_zhifubao_binding"]["binding_phone"]
        account_type = taobao_total_data["tb_zhifubao_binding"]["account_type"]
        verified_name = taobao_total_data["tb_zhifubao_binding"]["verified_name"]
        verified_id_card = taobao_total_data["tb_zhifubao_binding"]["verified_id_card"]
        zhifubaoinfo = ZhiFuBaoInfo(user_id=user_id,
                                    zhifubao_account=zhifubao_account,
                                    balance=balance,
                                    total_profit=total_profit,
                                    total_quotient=total_quotient,
                                    huabei_credit_amount=huabei_credit_amount,
                                    huabei_total_credit_amount=huabei_total_credit_amount,
                                    binding_phone=binding_phone,
                                    account_type=account_type,
                                    verified_name=verified_name,
                                    verified_id_card=verified_id_card)
        try:
            zhifubaoinfo.save()
        except Exception as e:
            logger.error(e)
        return zhifubaoinfo

    def save_codeinfo(self, user_id, code_url, code_status, code_status_message):
        # 保存二维码的相关信息
        codeinfo = CodeInfo(user_id=user_id, code_url=code_url, code_status=code_status,
                            code_status_message=code_status_message)
        try:
            codeinfo.save()
        except Exception as e:
            logger.error(e)
        return codeinfo

    def get_code_info(self, user_id):
        # 获取二维码的状态
        num = 0
        while num <= 8:
            code_obj = CodeInfo.objects.filter(user_id=user_id)
            if len(code_obj) > 0:
                code_obj = code_obj[0]
                return code_obj
            time.sleep(1)
            num += 1
        return None

    def get_code_obj(self, user_id):
        # 当用户访问时判断用户唯一性
        try:
            code_obj = CodeInfo.objects.filter(user_id=user_id)
            if len(code_obj) > 0:
                return {"res": 0}
            else:
                return {"res": 1}
        except Exception as e:
            logger.error(e)


class UserInfo(models.Model):
    # 定义user的个人账户信息
    user_id = models.CharField(max_length=40, verbose_name="用户id")
    login_name = models.CharField(max_length=20, verbose_name="用户名")
    vip_level = models.CharField(max_length=20, null=True, verbose_name="会员等级")
    score = models.CharField(max_length=20, null=True, verbose_name="淘气值")
    rate_summary = models.CharField(max_length=10, null=True, verbose_name="好评率")
    email = models.CharField(max_length=40, null=True, verbose_name="登陆邮箱")
    binding_phone = models.CharField(max_length=20, null=True, verbose_name="绑定的手机号")
    authentication = models.CharField(max_length=20, default="未完成", verbose_name="是否已完成身份验证")
    name = models.CharField(max_length=40, null=True, verbose_name="真实姓名")
    address = models.CharField(max_length=120, null=True, verbose_name="详细地址")
    tianmao_grade = models.CharField(max_length=20, null=True, verbose_name="天猫积分")

    class Meta:
        db_table = 'user_info'


class OrderInfo(models.Model):
    # 定义用户订单信息
    user_id = models.CharField(max_length=40, verbose_name="用户id")
    order_id = models.CharField(max_length=40, null=True, verbose_name="用户订单号")
    status = models.CharField(max_length=40, null=True, verbose_name="订单状态")
    actual_yuan = models.CharField(max_length=40, null=True, verbose_name="订单金额")
    phone_order = models.CharField(max_length=20, null=True, verbose_name="是否为手机订单")
    transaction_time = models.CharField(max_length=40, default="0000-00-00 00:00:00", verbose_name="成交时间")
    payment_time = models.CharField(max_length=40, default="0000-00-00 00:00:00", verbose_name="付款时间")
    confirmation_time = models.CharField(max_length=40, default="0000-00-00 00:00:00", verbose_name="确认时间")
    receiver_name = models.CharField(max_length=40, null=True, verbose_name="收货人")
    receiver_telephone = models.CharField(max_length=20, null=True, verbose_name="收货人手机号")
    receiver_address = models.CharField(max_length=120, null=True, verbose_name="收货地址")

    class Meta:
        db_table = 'order_info'


class ProductInfo(models.Model):
    # 定义商品信息
    user_id = models.CharField(max_length=40, verbose_name="用户id")
    order_id = models.CharField(max_length=40, null=True, verbose_name="用户订单号")
    product_name = models.CharField(max_length=240, null=True, verbose_name="商品名称")
    product_price = models.CharField(max_length=40, null=True, verbose_name='商品总额')
    product_quantity = models.CharField(max_length=20, null=True, verbose_name="商品数量")

    class Meta:
        db_table = 'product_info'


class DeliverAddrsInfo(models.Model):
    # 用户多个收货地址
    user_id = models.CharField(max_length=40, verbose_name="用户id")
    receiver_name = models.CharField(max_length=40, null=True, verbose_name="收件人")
    area = models.CharField(max_length=80, null=True, verbose_name="所在地区")
    address = models.CharField(max_length=120, null=True, verbose_name="详细地址")
    zip_code = models.CharField(max_length=20, null=True, verbose_name="邮政编码")
    phone = models.CharField(max_length=20, null=True, verbose_name="收货人手机号")
    is_default_address = models.CharField(max_length=40, null=True, verbose_name="是否为默认地址")

    class Meta:
        db_table = 'deliveraddrs_info'


class ZhiFuBaoInfo(models.Model):
    # 获取账户的支付宝信息
    user_id = models.CharField(max_length=40, verbose_name="用户id")
    zhifubao_account = models.CharField(max_length=40, null=True, verbose_name="支付宝账户")
    balance = models.CharField(max_length=40, null=True, verbose_name='支付宝余额')
    total_profit = models.CharField(max_length=40, null=True, verbose_name='余额宝累计收益')
    total_quotient = models.CharField(max_length=40, null=True, verbose_name='余额宝余额')
    huabei_credit_amount = models.CharField(max_length=40, null=True, verbose_name='花呗可用额度')
    huabei_total_credit_amount = models.CharField(max_length=40, null=True, verbose_name='花呗总额度')
    binding_phone = models.CharField(max_length=20, null=True, verbose_name="收货人手机号")
    account_type = models.CharField(max_length=20, null=True, verbose_name="账户类型")
    verified_name = models.CharField(max_length=40, null=True, verbose_name="实名认证的姓名")
    verified_id_card = models.CharField(max_length=40, null=True, verbose_name="身份证号")

    class Meta:
        db_table = 'zhifubao_info'


class CodeInfo(models.Model):
    # 保存二维码的状态
    user_id = models.CharField(max_length=40, verbose_name="用户id", unique=True)
    code_url = models.CharField(max_length=100, verbose_name="二维码url")
    code_status = models.CharField(max_length=20, verbose_name="二维码获取状态")
    code_status_message = models.CharField(max_length=40, verbose_name="二维码状态信息")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='二维码创建时间')

    class Meta:
        db_table = 'code_info'
