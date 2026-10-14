#include <Arduino.h>
#include "driver/twai.h"

#define CAN_TX_PIN GPIO_NUM_5  // D4 -> CAN(CTX)
#define CAN_RX_PIN GPIO_NUM_6  // D5 -> CAN(CRX)

#define CMD_SET_AXIS_REQUESTED_STATE 0x007
#define CMD_SET_INPUT_TORQUE        0x00E  // ★追加: トルク制御用ID

uint32_t get_can_id(uint32_t node_id, uint32_t cmd_id) {
    return (node_id << 5) | cmd_id;
}

void send_axis_state(uint32_t node_id, uint32_t state) {
    twai_message_t message;
    message.identifier = get_can_id(node_id, CMD_SET_AXIS_REQUESTED_STATE);
    message.extd = 0;
    message.rtr = 0;
    message.data_length_code = 4;
    message.data[0] = state & 0xFF;
    message.data[1] = (state >> 8) & 0xFF;
    message.data[2] = (state >> 16) & 0xFF;
    message.data[3] = (state >> 24) & 0xFF;
    twai_transmit(&message, pdMS_TO_TICKS(100));
}

// ★追加: トルク指令送信関数
void send_input_torque(uint32_t node_id, float torque) {
    twai_message_t message;
    message.identifier = get_can_id(node_id, CMD_SET_INPUT_TORQUE);
    message.extd = 0;
    message.rtr = 0;
    message.data_length_code = 4; // トルクは float (4バイト) のみ
    
    uint8_t* torque_bytes = (uint8_t*)&torque;
    for (int i = 0; i < 4; i++) {
        message.data[i] = torque_bytes[i];
    }
    twai_transmit(&message, pdMS_TO_TICKS(100));
}

void setup() {
    Serial.begin(115200);
    delay(1000);

    twai_general_config_t g_config = TWAI_GENERAL_CONFIG_DEFAULT(CAN_TX_PIN, CAN_RX_PIN, TWAI_MODE_NORMAL);
    twai_timing_config_t t_config = TWAI_TIMING_CONFIG_250KBITS();
    twai_filter_config_t f_config = TWAI_FILTER_CONFIG_ACCEPT_ALL();
    
    twai_driver_install(&g_config, &t_config, &f_config);
    twai_start();
    
    Serial.println("ESP32 CAN Bridge (Torque Mode) Ready.");
}

void loop() {
    // ラズパイからのコマンド解析
    // フォーマット例: "T 0 0.5\n" (Node 0 に 0.5 Nm のトルク指令)
    // フォーマット例: "S 0 8\n"   (状態変更)
    if (Serial.available()) {
        char cmd = Serial.read();
        if (cmd == 'T') {
            int node = Serial.parseInt();
            float torque = Serial.parseFloat();
            send_input_torque(node, torque);
            Serial.printf("Torque Command -> Node: %d, Torque: %.2f Nm\n", node, torque);
        } else if (cmd == 'S') {
            int node = Serial.parseInt();
            int state = Serial.parseInt();
            send_axis_state(node, state);
            Serial.printf("State Command -> Node: %d, State: %d\n", node, state);
        }
    }
}