# 子设备MQTT接入协议

对于子设备通过父设备（如网关）与EZtCloud通信的场景，父设备可使用以下MQTT主题：

## **主题概览**

以下主题用于子设备通过父设备与云端通讯：

| ***消息类型*** | ***主题*** | ***发布/订阅*** |
| --- | --- | --- |
| [上报子设备上线通知](#上报子设备上线通知) | sub_connect/{username} | 父设备发布 |
| [上报子设备下线通知](#上报子设备下线通知) | sub_disconnect/{username} | 父设备发布 |
| [上报子设备属性](#上报子设备属性) | sub_attributes/{username} | 父设备发布 |
| [上报子设备属性的响应](#上报子设备属性的响应) | sub_attributes_response/{username} | 父设备订阅 |
| [获取子设备云端属性](#获取子设备云端属性) | sub_attributes_get/{username} | 父设备发布 |
| [获取子设备云端属性的响应](#获取子设备云端属性的响应) | sub_attributes_get_response/{username} | 父设备订阅 |
| [云端下发属性至子设备](#云端下发属性至子设备) | sub_attributes_push/{username} | 父设备订阅 |
| [上报子设备事件](#上报子设备事件) | sub_event_report/{username} | 父设备发布 |
| [上报子设备事件的响应](#上报子设备事件的响应) | sub_event_response/{username} | 父设备订阅 |
| [云端下发命令至子设备](#云端下发命令至子设备) | sub_command_send/{username} | 父设备订阅 |
| [云端下发命令至子设备的响应](#云端下发命令至子设备的响应) | sub_command_reply/{username} | 父设备发布 |

## **各主题的使用方法**

下面我们逐个介绍各个主题的使用方法。

### **上报子设备上线通知**

当父设备确定子设备已连接时，可上报消息通知平台，父设备发布主题如下：

***sub_connect/{username}***

```json
{
  "device": ["SUB_DEVICE_ADDR", "SUB_SUB_DEVICE_ADDR"],
  "product": "ProductKey OR ProductCode"
}
```

`device`：必含。子设备地址。它是一个列表，其中第0个元素表示本级子设备的子设备地址，第1个元素表示再下1级子设备的子设备地址，第2个元素表示再下2级子设备的子设备地址，依次类推。它至少应包含一个元素。

`product`：非必含。`EZtCloud 公共产品库` 中，产品的 `产品Key` 或 `产品识别码` 。当包含此参数时，EZtCloud 将检查该设备是否已被创建，若否，则自动创建该设备。

### **上报子设备下线通知**

当父设备确定子设备已断开时，可上报消息通知平台，父设备发布主题如下：

***sub_disconnect/{username}***

发布消息格式如下：

```json
{
  "device": ["SUB_DEVICE_ADDR", "SUB_SUB_DEVICE_ADDR"]
}
```

`device`：必含。子设备地址。它是一个列表，其中第0个元素表示本级子设备的子设备地址，第1个元素表示再下1级子设备的子设备地址，第2个元素表示再下2级子设备的子设备地址，依次类推。它至少应包含一个元素。

### **上报子设备属性**

当父设备接收到子设备的属性变化时，向平台上报子设备属性主题如下：

***sub_attributes/{username}***

EZtCloud支持如下2种消息格式：[树形格式](子设备MQTT接入协议.md)、[平铺格式](子设备MQTT接入协议.md)。两者功能等效，设备商可自行选其一实现。

消息成功上发后，在控制台的设备详情页，会实时更新显示设备属性的最新值。

**树形格式：**

```json
{
  "SUB_DEVICE_ADDR_1": {
    "attributes": {
      "ATTRIBUTES1": "VALUE1",
      "ATTRIBUTES2": "VALUE2"
    },
    // 属性时间戳，可选。不提供则记录为服务器时间
    "ts": 12312314212,
    "sub": {
      "SUB_DEVICE_ADDR_1_1": {
        "attributes": {
          "ATTRIBUTES1": "VALUE1",
          "ATTRIBUTES2": "VALUE2"
        },
        // 属性时间戳，可选。不提供则记录为服务器时间
        "ts": 12312314211,
        "sub": {
          // 可递归包含子设备
        }
      },
      "SUB_DEVICE_ADDR_1_2": {
        "attributes": {
          "ATTRIBUTES1": "VALUE1",
          "ATTRIBUTES2": "VALUE2"
        }
        // sub 可为空，也可不含该键
        // "sub": {}
      }
    }
  },
  "SUB_DEVICE_ADDR_2": {
    // attributes 可为空，也可不含该键
    // "attributes": {}
    "sub": {
      "SUB_DEVICE_ADDR_2_1": {
        "attributes": {
          "ATTRIBUTES1": "VALUE1",
          "ATTRIBUTES2": "VALUE2"
        }
      }
    }
  }
}
```

任何设备支持一次上报多个子设备的属性。

`SUB_DEVICE_ADDR1`、`SUB_DEVICE_ADDR2`：子设备地址。

`SUB_DEVICE_ADDR_1_1`、`SUB_DEVICE_ADDR_1_2`：子设备SUB_DEVICE_ADDR1的子设备地址。

`ATTRIBUTES1`、`ATTRIBUTES2`

举例，某设备上报多个子设备的属性，如下：

```json
{
  "1": {
    "attributes":{
      "battery": 100,
      "occupancy": false
    },
    "sub": {
      "2": {
        "attributes": {
          "battery": 98,
          "occupancy": true
        }
      }
    }
  }
}
```

其中，`"1"`是当前设备的直接子设备，而`"2"`是`"1"`的子设备。

**平铺格式：**

```json
[
  {
    "device": ["SUB_DEVICE_ADDR_1"],
    "ts": 12312314212,
    "attributes": {
      "ATTRIBUTES1": "VALUE1",
      "ATTRIBUTES2": "VALUE2"
    }
  },
  {
    "device": ["SUB_DEVICE_ADDR_1", "SUB_DEVICE_ADDR_1_1"],
    "ts": 12312314211,
    "attributes": {
      "ATTRIBUTES1": "VALUE1",
      "ATTRIBUTES2": "VALUE2"
    },
  },
  {
    "device": ["SUB_DEVICE_ADDR_1", "SUB_DEVICE_ADDR_1_2"],
    "ts": 12312314211,
    "attributes": {
      "ATTRIBUTES1": "VALUE1",
      "ATTRIBUTES2": "VALUE2"
    },
  },
  {
    "device": ["SUB_DEVICE_ADDR_2", "SUB_DEVICE_ADDR_2_1"],
    "attributes": {
      "ATTRIBUTES1": "VALUE1",
      "ATTRIBUTES2": "VALUE2"
    },
  }
]
```

举例，某设备上报多个子设备的属性，如下：

```json
[
  {
    "device": ["1"],
    "attributes":{
      "battery": 100,
      "occupancy": false
    },
  },
  {
    "device": ["1", "2"],
    "attributes": {
       "battery": 98,
       "occupancy": true
    }
  }
]
```

> **💡 提示**
>
> 上述两种格式中的示例是完全等效的。

### **上报子设备属性的响应**

作为父设备的[**直接上网设备**](设备联网方式.md)订阅这个主题，可以实时接收到平台对[**上报子设备属性**](子设备MQTT接入协议.md)的反馈消息。

***sub_attributes_response/{username}***

接收到的消息格式如下：

```json
{
  "error_code": 0,
  "error_msg": "OK",
  "ts": 12312314212
}
```

`error_code` :  错误码。0表示成功，非0表示失败。

`error_msg` : 错误信息。以字符串形式，对错误进行详细说明。

`ts` : 云平台发送本消息时的时间戳。

> **⚠️ 注意**
>
> 此响应消息默认`不开启`，需要时可在此处开启：`设备类型详情页` > `设置` > `云端响应`。

### **获取子设备云端属性**

父设备可以获取子设备在平台的属性，如下为典型的使用本主题的场景：父设备初始化子设备时，从云平台获取状态或配置信息。

发布主题如下：

***sub_attributes_get/{username}***

发布的消息格式

```json
{
  "device": ["SUB_DEVICE_ADDR", "SUB_SUB_DEVICE_ADDR"],
  "get": {
    "keys": ["KEY1", "KEY2"]
  }
}
```

`device`：必含。子设备地址。它是一个列表，其中第0个元素表示本级子设备的子设备地址，第1个元素表示再下1级子设备的子设备地址，第2个元素表示再下2级子设备的子设备地址，依次类推。它至少应包含一个元素。

`keys`：要读取的属性标识符数组，空数组 [ ] 标识读取所有属性。

### **获取子设备云端属性的响应**

父设备订阅以下主题，以接收平台回复的子设备属性。

***sub_attributes_get_response/{username}***

回复的消息格式

```json
{
  "device": ["SUB_DEVICE_ADDR", "SUB_SUB_DEVICE_ADDR"],
  "error_code": 0,
  "error_msg": "",
  "ts": 12312314212,
  "attributes": {
    "KEY1": "VALUE1",
    "KEY1": "VALUE2"
  }
}
```

`device`：子设备地址。它是一个列表，其中第0个元素表示本级子设备的子设备地址，第1个元素表示再下1级子设备的子设备地址，第2个元素表示再下2级子设备的子设备地址，依次类推。它至少应包含一个元素。

`error_code` :  错误码。0表示成功，非0表示失败。

`error_msg` : 错误信息。以字符串形式，对错误进行详细说明。

`ts` : 云平台发送本消息时的时间戳。

`attributes`：读取到的子设备属性。

### **云端下发属性至子设备**

除了子设备主动获取属性以外，我们也需要让子设备可以实时接收云平台下发的属性。

确保父设备已订阅如下主题：

***sub_attributes_push/{username}***

当云平台下发属性给子设备时，父设备会通过以上订阅主题，收到 JSON 结构的消息，例如：

```json
{
  "device": ["SUB_DEVICE_ADDR", "SUB_SUB_DEVICE_ADDR"],
  "attributes": {
    "switch": false
  }
}
```

`device`：子设备地址。它是一个列表，其中第0个元素表示本级子设备的子设备地址，第1个元素表示再下1级子设备的子设备地址，第2个元素表示再下2级子设备的子设备地址，依次类推。它至少应包含一个元素。

`attributes`：读取到的子设备属性。

这个示例消息显然是通知子设备关闭某个开关，子设备通过自身的程序实现该功能后，可以接着向云平台上报属性或上报事件，让云平台得到确认。

### **上报子设备事件**

在前边的介绍中，我们已经知道，事件通常用于设备向平台发送一些通知或请求，但不希望将相关参数记录到设备属性中。

父设备同样可以上报子设备的事件，并触发平台对子设备设置的事件规则。

例如，父设备上报子设备请求 OTA 固件版本检查的事件。

发布主题如下：

***sub_event_report/{username}***

上报的消息格式

`device`：子设备地址。它是一个列表，其中第0个元素表示本级子设备的子设备地址，第1个元素表示再下1级子设备的子设备地址，第2个元素表示再下2级子设备的子设备地址，依次类推。它至少应包含一个元素。

`event`：事件消息体，与直连设备事件上报的格式相同。

### **上报子设备事件的响应**

如果我们想知道事件上报是否被云平台成功接收，可以订阅如下主题：

***sub_event_response/{username}***

当父设备上报子设备事件后，便会通过该主题收到来自云端的响应消息，如果云端接收成功，响应消息如下：

```json
{
  "error_code": 0,
  "error_msg": "OK",
  "ts": 12312314212,
  "device": "SUB_DEVICE_ADDR1"
}
```

> **💡 提示**
>
> 响应消息中的成功，只代表云平台成功收到了事件上报，并不代表对事件进行业务处理的结果。

云平台收到子设备的事件上报后，如何处理事件呢？***规则引擎*** 便派上用场了，通过规则引擎，您可以将事件实时推送到第三方，或通过规则引擎的云函数实现告警策略，当然还可以实现对其它设备的联动控制。

> **⚠️ 注意**
>
> 此响应消息默认`不开启`，需要时可在此处开启：`设备类型详情页` > `设置` > `云端响应`。

### **云端下发命令至子设备**

订阅主题如下：

***sub_command_send/{username}***

接收到的消息格式如下：

```json
{
  "device": "SUB_DEVICE_ADDR1",
  "command": {
    "method": "COMMAND_IDENTIFIER",
    "params": {
      "PARAM1": "VALUE1",
      "PARAM2": "VALUE2"
    },
    "id": 1000
  }
}
```

`device`：子设备地址。

`command`：命令消息体，与直连设备下发命令消息的格式相同。

### **云端下发命令至子设备的响应**

子设备收到命令消息后，在设备端实现特定的功能前，可以回复命令，也可以不回复命令。

云端会自动接收回复命令，并和下发命令进行匹配，在控制台的设备命令历史中，您可以看到一组包含下发和回复的命令日志。一次下发命令只能接收一次回复命令，它们的匹配是通过使用一致的 `id` 来保证。

发布主题如下：

***sub_command_reply/{username}***

消息格式如下：

```json
{
  "device": "SUB_DEVICE_ADDR1",

  "command": {
    "method": "EVENT_IDENTIFIER",
    "params": {
      "PARAM1": "VALUE1",
      "PARAM2": "VALUE2"
    },
    "id": 1000
  }
}
```

它和命令下发的消息内容完全一样。