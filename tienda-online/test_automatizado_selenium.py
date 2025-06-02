from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
import time
import os

# Directorio donde se encuentra el chromedriver.exe
DRIVER_DIRECTORY = "C:\\SeleniumDrivers"
# Nombre del archivo ejecutable de ChromeDriver
CHROME_DRIVER_FILENAME = "chromedriver.exe"
# Ruta completa al chromedriver
CHROMEDRIVER_PATH = os.path.join(DRIVER_DIRECTORY, CHROME_DRIVER_FILENAME)

# URLs de la aplicación
APP_BASE_URL = "http://127.0.0.1:5000/"
LOGIN_PAGE_URL = APP_BASE_URL + "login"
REGISTER_PAGE_URL = APP_BASE_URL + "registro" # Asumiendo esta es la URL de registro

# Selectores de elementos

REGISTER_LINK_CSS = ".auth-links p a[href*='registro']"
USERNAME_INPUT_NAME = "usuario"
EMAIL_INPUT_NAME = "email"
PASSWORD_INPUT_NAME = "password"
AUTH_BUTTON_CLASS = "auth-btn"

# pagra producto
CATEGORY_FILTER_ID = "categoryFilter"
ADD_CART_BUTTON_CLASS = "add-cart-btn"
CART_LINK_CSS = "a[href*='/carrito']"

#paguina del carrito
CART_CONTAINER_CLASS = "carrito-container"
CHECKOUT_BUTTON_CLASS = "checkout-btn"

# Modalidad de pago
PAYMENT_MODAL_ID = "modalPago"
PAY_BY_CARD_BUTTON_XPATH = "//button[contains(text(),'Pago por tarjeta')]"
CARD_SECTION_ID = "tarjeta-section"
PRINT_INVOICE_BUTTON_XPATH = "//button[contains(text(),'Imprimir Factura')]"
CLOSE_MODAL_BUTTON_CLASS = "close"

# Tiempo de espera máximo para elementos (segundos)
DEFAULT_TIMEOUT = 25


def setup_driver():
    """Configura e inicia el WebDriver de Chrome."""
    if not os.path.exists(CHROMEDRIVER_PATH):
        print(f"ERROR: chromedriver.exe no encontrado en {CHROMEDRIVER_PATH}")
        return None

    service = Service(executable_path=CHROMEDRIVER_PATH)
    try:
        driver = webdriver.Chrome(service=service)
        driver.maximize_window()
        print("Navegador Chrome iniciado exitosamente y maximizado.")
        return driver
    except Exception as e:
        print(f"ERROR: No se pudo iniciar Chrome. Mensaje: {e}")
        return None

def register_user(driver, wait):
    """Navega a la página de registro y crea un nuevo usuario."""
    print(f"\n--- INICIANDO PROCESO DE REGISTRO ---")
    print(f"Navegando a la URL de la página de login: {LOGIN_PAGE_URL}")
    driver.get(LOGIN_PAGE_URL)
    time.sleep(2) # Pequeña pausa inicial

    print("Buscando y haciendo clic en el enlace para registrarse...")
    register_link = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, REGISTER_LINK_CSS)),
                                message=f"ERROR: Enlace de registro (CSS Selector: '{REGISTER_LINK_CSS}') no encontrado o no clickeable.")
    register_link.click()
    print("Redirigido a la página de registro.")
    time.sleep(2) # Pausa para asegurar que la página de registro cargue

    print("Intentando realizar el registro de un nuevo usuario...")
    # Generar credenciales únicas
    timestamp = str(int(time.time()))
    new_username = f"testuser_{timestamp}"
    new_email = f"testemail_{timestamp}@example.com"
    new_password = "securepassword123"

    register_username_input = wait.until(EC.presence_of_element_located((By.NAME, USERNAME_INPUT_NAME)),
                                            message=f"ERROR: Campo de usuario '{USERNAME_INPUT_NAME}' no encontrado en la página de registro.")
    register_email_input = driver.find_element(By.NAME, EMAIL_INPUT_NAME)
    register_password_input = driver.find_element(By.NAME, PASSWORD_INPUT_NAME)
    register_button = driver.find_element(By.CLASS_NAME, AUTH_BUTTON_CLASS)

    print(f"Registrando con: Usuario='{new_username}', Email='{new_email}', Contraseña='{new_password}'")
    register_username_input.send_keys(new_username)
    register_email_input.send_keys(new_email)
    register_password_input.send_keys(new_password)
    register_button.click()
    print("Credenciales de registro enviadas y clic en 'Registrarse'. Esperando redirección...")
    time.sleep(3) # Pausa aumentada para que el servidor procese el registro y redirija

    # Verificar redirección después del registro
    try:
        wait.until(EC.any_of(
            EC.url_to_be(LOGIN_PAGE_URL),
            EC.url_contains('/productos'),
            EC.url_contains('/')
        ), message="ERROR: La URL no cambió a la esperada después del registro.")
        print(f"URL actual después del registro: {driver.current_url}")
        print("Página de login/productos cargada correctamente después del registro.")
    except Exception as e:
        print(f"ADVERTENCIA: Redirección post-registro no fue la esperada. Intentando navegar a {LOGIN_PAGE_URL}. Mensaje: {e}")
        driver.get(LOGIN_PAGE_URL)
        wait.until(EC.presence_of_element_located((By.NAME, USERNAME_INPUT_NAME)),
                   message=f"ERROR: No se encontró el campo de usuario '{USERNAME_INPUT_NAME}' después de navegar al login explícitamente.")
        print("Navegación manual a la página de login exitosa.")
    
    return new_username, new_password

def login_user(driver, wait, username, password):
    """Realiza el login con las credenciales dadas."""
    print(f"\n--- INICIANDO PROCESO DE LOGIN ---")
    print(f"Intentando realizar el login con usuario '{username}'...")
    driver.get(LOGIN_PAGE_URL) # Asegurarse de estar en la página de login
    time.sleep(2)

    login_username_input = wait.until(EC.presence_of_element_located((By.NAME, USERNAME_INPUT_NAME)),
                                        message=f"ERROR: Campo de usuario '{USERNAME_INPUT_NAME}' no encontrado en la página de login para iniciar sesión.")
    login_password_input = driver.find_element(By.NAME, PASSWORD_INPUT_NAME)
    login_button = driver.find_element(By.CLASS_NAME, AUTH_BUTTON_CLASS)

    login_username_input.send_keys(username)
    login_password_input.send_keys(password)
    login_button.click()
    print("Credenciales de login enviadas. Esperando redirección a la página de productos...")
    time.sleep(3)

    wait.until(EC.presence_of_element_located((By.ID, CATEGORY_FILTER_ID)),
               message=f"ERROR: El filtro de categoría ('{CATEGORY_FILTER_ID}') no se encontró. Posiblemente el login falló o la página de productos no cargó correctamente.")
    print("En la página de productos. Login exitoso.")

def add_product_to_cart(driver, wait, category="consolas"):
    """Filtra productos y añade el primero visible al carrito."""
    print(f"\n--- AÑADIENDO PRODUCTO AL CARRITO ---")
    print(f"Filtrando productos por categoría '{category}'...")
    category_select = Select(driver.find_element(By.ID, CATEGORY_FILTER_ID))
    category_select.select_by_value(category)
    time.sleep(2) # Pausa breve para que el filtro se aplique

    print("Buscando y agregando el primer producto visible al carrito...")
    add_cart_buttons = driver.find_elements(By.CLASS_NAME, ADD_CART_BUTTON_CLASS)
    added_to_cart = False
    for btn in add_cart_buttons:
        if btn.is_displayed() and btn.is_enabled():
            btn.click()
            added_to_cart = True
            print("Producto agregado al carrito.")
            break

    if not added_to_cart:
        print("ADVERTENCIA: No se encontró ningún botón 'add-cart-btn' visible para añadir al carrito.")
        raise Exception("No se pudo añadir ningún producto al carrito.")

def complete_payment(driver, wait):
    """Navega al carrito y completa el proceso de pago."""
    print(f"\n--- COMPLETANDO PROCESO DE PAGO ---")
    print("Navegando a la página del carrito...")
    cart_link = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, CART_LINK_CSS)),
                            message=f"ERROR: Enlace 'carrito' (CSS Selector: '{CART_LINK_CSS}') no encontrado o no clickeable.")
    cart_link.click()
    time.sleep(2)

    print("En la página del carrito. Verificando el contenedor principal.")
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, CART_CONTAINER_CLASS)),
                message=f"ERROR: Contenedor '{CART_CONTAINER_CLASS}' no encontrado en la página del carrito.")

    print("Procediendo al pago...")
    pay_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, CHECKOUT_BUTTON_CLASS)),
                            message=f"ERROR: Botón '{CHECKOUT_BUTTON_CLASS}' para pagar no encontrado o no clickeable.")
    pay_button.click()
    time.sleep(1)

    print("Esperando que el modal de pago sea visible...")
    modal = wait.until(EC.visibility_of_element_located((By.ID, PAYMENT_MODAL_ID)),
                        message=f"ERROR: Modal de pago ('{PAYMENT_MODAL_ID}') no encontrado o no visible.")

    print("Seleccionando 'Pago por tarjeta'...")
    pago_tarjeta_btn = wait.until(EC.element_to_be_clickable((By.XPATH, PAY_BY_CARD_BUTTON_XPATH)),
                                    message=f"ERROR: Botón 'Pago por tarjeta' no encontrado o no clickeable.")
    pago_tarjeta_btn.click()
    time.sleep(1)

    print("Esperando que aparezca la sección de pago por tarjeta...")
    wait.until(EC.visibility_of_element_located((By.ID, CARD_SECTION_ID)),
                message=f"ERROR: Sección de tarjeta ('{CARD_SECTION_ID}') no encontrada después de seleccionar el pago.")

    print("Haciendo clic en 'Imprimir Factura'...")
    imprimir_factura_btn = wait.until(EC.element_to_be_clickable((By.XPATH, PRINT_INVOICE_BUTTON_XPATH)),
                                        message=f"ERROR: Botón 'Imprimir Factura' no encontrado o no clickeable.")
    imprimir_factura_btn.click()
    time.sleep(3) # Pausa breve para que la acción de imprimir se procese

    print("Cerrando el modal de pago...")
    close_modal_btn = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, CLOSE_MODAL_BUTTON_CLASS)),
                                    message=f"ERROR: Botón para cerrar el modal ('{CLOSE_MODAL_BUTTON_CLASS}') no encontrado o no clickeable.")
    close_modal_btn.click()
    print("Modal de pago cerrado.")
    time.sleep(2)

# --- 3. FLUJO PRINCIPAL DE LA AUTOMATIZACIÓN ---
if __name__ == "__main__":
    driver = None # Inicializar driver a None
    try:
        driver = setup_driver()
        if driver is None:
            exit()

        wait = WebDriverWait(driver, DEFAULT_TIMEOUT)

        # Paso 1: Registrar un nuevo usuario
        new_username, new_password = register_user(driver, wait)

        # Paso 2: Iniciar sesión con el usuario recién registrado
        login_user(driver, wait, new_username, new_password)

        # Paso 3: Añadir un producto al carrito (ej. de categoría 'consolas')
        add_product_to_cart(driver, wait, "consolas")

        # Paso 4: Completar el proceso de pago
        complete_payment(driver, wait)

        print("\n--- AUTOMATIZACIÓN COMPLExTADA EXITOSAMENTE ---")
        print("El navegador se cerrará en breve.")
        time.sleep(3)

    except Exception as e:
        print("\n--- ¡HA OCURRIDO UN ERROR DURANTE LA AUTOMATIZACIÓN! ---")
        print(f"Tipo de error: {type(e).__name__}")
        print(f"Mensaje del error: {e}")
        print("\n*POSIBLES CAUSAS Y SOLUCIONES (¡REVISAR CON ATENCIÓN!):*")
        print("1. *StaleElementReferenceException:* Un elemento fue encontrado, pero la página se actualizó o recargó, invalidando su referencia. La solución más común es volver a localizar el elemento justo antes de usarlo (especialmente si es un clic o una interacción posterior a una acción).")
        print("2. *Tu aplicación web (servidor) NO está corriendo.* Asegúrate de haberla iniciado en otra terminal y que sea accesible manualmente en http://127.0.0.1:5000/.")
        print("3. *Las credenciales de login o registro son incorrectas/ya existen.* Verifica las credenciales en tu script y pruébalas manualmente en el navegador.")
        print("4. *Un elemento NO fue encontrado a tiempo (TimeoutException):* Esto suele indicar que una acción anterior (ej. login/registro) falló o que la página cambió su estructura HTML.")
        print("5. *La versión de ChromeDriver NO coincide con la versión de tu navegador Chrome.*")
        print("6. *Problemas de red o firewall.*")
        print("7. *Selectores de elementos HTML han cambiado:* Revisa que los 'By.ID', 'By.NAME', 'By.CLASS_NAME', 'By.CSS_SELECTOR', 'By.XPATH' sigan siendo válidos para tu aplicación.")

        try:
            if driver:
                screenshot_path = "error_screenshot.png"
                driver.save_screenshot(screenshot_path)
                print(f"Captura de pantalla del error guardada en: {os.path.abspath(screenshot_path)}")
        except Exception as screenshot_error:
            print(f"No se pudo tomar la captura de pantalla del error: {screenshot_error}")

    finally:
        if driver:
            driver.quit()
            print("Navegador cerrado.")