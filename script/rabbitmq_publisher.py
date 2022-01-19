"""
rabbitmq 生产者demo
1.简单模式: 最简单的一对一模式
2.工作队列模式: 一对多模式,一个生产者多个消费者,每条消息仅能被其中的一个消费者消费
    轮询分发: 将消息轮流发给每个消费者,一个消费者处理完才会发送下一个.例: A消费第1,4,7..条消息, B消费第2,5,8..条消息, C消费3,6,9...条消息
    公平分发: 只要有消费者处理完就会把下一条发给空闲的消费者
3.发布/订阅模式(fanout): 生产者将消息发送给broker,由交换机将消息转发到绑定此交换机的每个队列,每个绑定交换机的队列都将接收到消息.消费者监听自己的队列并进行消费
4.路由模式(direct): 生产者将消息发送给 broker,由交换机根据 routing_key 分发到不同的消息队列,然后消费者同样根据 routing_key 来消费对应队列上的消息.
5.主题模式(topic): 主题模式应该算是路由模式的一种,routing_key支持正则表达式
6.RPC模式: 通过消息队列来实现 RPC 功能,客户端发送消息到消费队列,消息内容其实就是服务端执行需要的参数,服务端消费消息内容,执行程序,然后将结果返回给客户端

channel: 信道是生产者,消费者和 RabbitMQ 通信的渠道,是建立在 TCP 连接上的虚拟连接.一个 TCP 连接上可以建立成百上千个信道,通过这种方式,可以减少系统开销,提高性能.
Broker: 接收客户端连接,实现 AMQP 协议的消息队列和路由功能的进程.
Virtual Host: 虚拟主机的概念,类似权限控制组,一个 Virtual Host 里可以有多个 Exchange 和 Queue,权限控制的最小粒度是 Virtual Host.
Exchange: 交换机,接收生产者发送的消息,并根据 Routing Key 将消息路由到服务器中的队列 Queue.
ExchangeType: 交换机类型决定了路由消息的行为,RabbitMQ 中有三种 Exchange 类型,分别是 direct、fanout、topic.
Message Queue: 消息队列,用于存储还未被消费者消费的消息,由 Header 和 body 组成.
        Header 是由生产者添加的各种属性的集合,包括 Message 是否被持久化、优先级是多少、由哪个 Message Queue 接收等,body 是真正需要发送的数据内容.
BindingKey: 绑定关键字,将一个特定的 Exchange 和一个特定的 Queue 绑定起来.
"""
import pika
import json
import datetime
import time


class TestPublisher(object):

    def __init__(self):
        self.username = 'sanford'
        self.password = '123456'
        self.host = 'localhost'
        self.port = 5672
        self.virtual_host = 'sanford_host'

    def publisher_00(self, msg_type, data):
        """
        简单模式/工作队列模式
        """
        # 创建连接时的登录凭证
        credentials = pika.PlainCredentials(username=self.username, password=self.password)

        # 参数设置
        params = pika.ConnectionParameters(host=self.host,
                                           port=self.port,
                                           virtual_host=self.virtual_host,
                                           credentials=credentials)

        # 创建阻塞式连接
        connection = pika.BlockingConnection(params)

        # 创建信道
        channel = connection.channel()

        # 声明队列 队列持久化: durable=True, 服务重启后队列依然存在
        channel.queue_declare(queue='queue_00', durable=True)

        # 消息属性设置 消息持久化: delivery_mode=2
        properties = pika.BasicProperties(headers={'msg-type': msg_type},
                                          delivery_mode=2)

        # exchange为默认''时routing_key为queue
        channel.basic_publish(exchange='',
                              routing_key='queue_00',
                              body=json.dumps(data),
                              properties=properties)

        connection.close()

    def publisher_01(self, msg_type, data):
        """
        发布/订阅模式(fanout)
        """
        credentials = pika.PlainCredentials(username=self.username, password=self.password)
        params = pika.ConnectionParameters(host=self.host,
                                           port=self.port,
                                           virtual_host=self.virtual_host,
                                           credentials=credentials)
        connection = pika.BlockingConnection(params)
        channel = connection.channel()

        # 声明交换机指定类型 交换机持久化: durable=True, 服务重启后交换机依然存在
        channel.exchange_declare(exchange='exchange_01', exchange_type='fanout', durable=True)

        properties = pika.BasicProperties(headers={'msg-type': msg_type},
                                          delivery_mode=2)

        channel.basic_publish(exchange='exchange_01',
                              routing_key='',
                              body=json.dumps(data),
                              properties=properties)

        connection.close()


if __name__ == '__main__':
    test_publisher = TestPublisher()

    # 简单模式/工作队列模式
    # msg_type_00 = 'msg_type_00'
    # for i in range(20):
    #     time.sleep(1)
    #     data_00 = {'id': i, 'name': 'jay', 'send_time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    #     test_publisher.publisher_00(msg_type_00, data_00)

    # 发布/订阅模式(fanout)
    msg_type_01 = 'msg_type_01'
    for i in range(20):
        time.sleep(1)
        data_01 = {'id': i, 'name': 'jay', 'send_time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        test_publisher.publisher_01(msg_type_01, data_01)
