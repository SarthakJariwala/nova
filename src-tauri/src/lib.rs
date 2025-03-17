// Learn more about Tauri commands at https://tauri.app/develop/calling-rust/
use serde_json::Value;
use std::sync::Mutex;
use tauri::{command, State};
use zmq;

struct ZmqContext(Mutex<Option<zmq::Context>>);
struct ZmqSocket(Mutex<Option<zmq::Socket>>);

#[command]
async fn connect_to_zmq_server(
    context_state: State<'_, ZmqContext>,
    socket_state: State<'_, ZmqSocket>,
) -> Result<(), String> {
    let mut context = context_state.0.lock().unwrap();
    let mut socket = socket_state.0.lock().unwrap();

    if socket.is_some() {
        return Ok(());
    }

    *context = Some(zmq::Context::new());
    if let Some(ctx) = context.as_ref() {
        match ctx.socket(zmq::REQ) {
            Ok(sock) => {
                if let Err(e) = sock.connect("tcp://localhost:5555") {
                    return Err(format!("Failed to connect: {}", e));
                }
                *socket = Some(sock);
                Ok(())
            }
            Err(e) => Err(format!("Failed to create socket: {}", e)),
        }
    } else {
        Err("Failed to create ZMQ context".to_string())
    }
}

#[command]
async fn send_zmq_request(
    method: String,
    params: String,
    socket_state: State<'_, ZmqSocket>,
) -> Result<String, String> {
    let socket = socket_state.0.lock().unwrap();

    if let Some(socket) = socket.as_ref() {
        let request = serde_json::json!({
            "method": method,
            "params": serde_json::from_str::<Value>(&params).unwrap_or(Value::Null),
        });

        let request_str = request.to_string();

        if let Err(e) = socket.send(&request_str, 0) {
            return Err(format!("Failed to send request: {}", e));
        }

        let mut response = zmq::Message::new();
        if let Err(e) = socket.recv(&mut response, 0) {
            return Err(format!("Failed to receive response: {}", e));
        }

        let response_str = response
            .as_str()
            .ok_or("Invalid response data".to_string())?
            .to_string();

        Ok(response_str)
    } else {
        Err("Not connected to server".to_string())
    }
}

#[command]
async fn disconnect_from_zmq_server(socket_state: State<'_, ZmqSocket>) -> Result<(), String> {
    let mut socket = socket_state.0.lock().unwrap();
    *socket = None;
    Ok(())
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_opener::init())
        .manage(ZmqContext(Mutex::new(None)))
        .manage(ZmqSocket(Mutex::new(None)))
        .invoke_handler(tauri::generate_handler![
            connect_to_zmq_server,
            send_zmq_request,
            disconnect_from_zmq_server,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
