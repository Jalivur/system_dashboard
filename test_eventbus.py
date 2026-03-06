#!/usr/bin/env python3
"""
Test rápido del EventBus para validar que funciona correctamente.
"""
import sys
sys.path.insert(0, '/home/jalivur/Documents/system_dashboard_develop')

from core.event_bus import get_event_bus, EventBus
import threading
import time

def test_eventbus():
    """Prueba básica del EventBus."""
    print("🧪 Test del EventBus\n")
    
    bus = get_event_bus()
    print("✅ EventBus instanciado correctamente\n")
    
    # Test 1: Publicar y suscribirse
    print("Test 1: Publish/Subscribe básico")
    events_received = []
    
    def callback(data):
        events_received.append(data)
        print(f"  ✓ Evento recibido: {data}")
    
    bus.subscribe("test.event1", callback)
    bus.publish("test.event1", {"valor": 42})
    bus.process_events()
    
    assert len(events_received) == 1, "No se recibió el evento"
    assert events_received[0]["valor"] == 42, "Datos incorrectos"
    print("  ✅ PASS\n")
    
    # Test 2: Thread-safety
    print("Test 2: Thread-safety")
    events_received.clear()
    
    def publish_from_thread():
        time.sleep(0.1)
        bus.publish("test.event2", {"from_thread": True})
    
    bus.subscribe("test.event2", callback)
    
    thread = threading.Thread(target=publish_from_thread, daemon=True)
    thread.start()
    time.sleep(0.2)
    
    bus.process_events()
    
    assert len(events_received) == 1, "No se recibió evento del thread"
    assert events_received[0]["from_thread"], "Datos incorrectos"
    print("  ✓ Thread publicó evento correctamente")
    print("  ✅ PASS\n")
    
    # Test 3: Múltiples suscriptores
    print("Test 3: Múltiples suscriptores")
    events_received.clear()
    callbacks_called = []
    
    def callback1(data):
        callbacks_called.append(1)
    
    def callback2(data):
        callbacks_called.append(2)
    
    bus.subscribe("test.event3", callback1)
    bus.subscribe("test.event3", callback2)
    bus.publish("test.event3", {"data": "test"})
    bus.process_events()
    
    assert len(callbacks_called) == 2, f"Se llamó {len(callbacks_called)} callbacks, esperaba 2"
    assert set(callbacks_called) == {1, 2}, "No se llamaron los callbacks correctos"
    print("  ✓ Ambos callbacks se ejecutaron")
    print("  ✅ PASS\n")
    
    # Test 4: Unsubscribe
    print("Test 4: Unsubscribe")
    bus.unsubscribe("test.event3", callback1)
    callbacks_called.clear()
    
    bus.publish("test.event3", {"data": "test"})
    bus.process_events()
    
    assert len(callbacks_called) == 1, f"Se llamó {len(callbacks_called)} callbacks, esperaba 1"
    assert callbacks_called[0] == 2, "Se ejecutó el callback incorrecto"
    print("  ✓ Callback1 fue desuscrito correctamente")
    print("  ✅ PASS\n")
    
    # Test 5: Singleton
    print("Test 5: Singleton")
    bus2 = get_event_bus()
    assert bus is bus2, "EventBus no es singleton"
    print("  ✓ EventBus es singleton")
    print("  ✅ PASS\n")
    
    print("=" * 50)
    print("✅ TODOS LOS TESTS PASARON")
    print("=" * 50)

if __name__ == "__main__":
    try:
        test_eventbus()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
