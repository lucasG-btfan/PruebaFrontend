Este proyecto consiste en un sistema completo de comercio electrónico desarrollado con arquitectura de microservicios. El sistema permite a los usuarios navegar por productos, realizar compras, gestionar su perfil y calificar productos. Los administradores tienen acceso a un panel de control para gestionar productos, órdenes y clientes.

🏗️ Arquitectura del Sistema

Backend (FastAPI + PostgreSQL)

text

backend/

├── controllers/          # Controladores de endpoints REST

├── models/              # Modelos de base de datos SQLAlchemy

├── schemas/             # Esquemas de validación Pydantic

├── services/            # Lógica de negocio

├── repositories/        # Patrón Repository para acceso a datos

├── middleware/          # Middleware de autenticación y seguridad

├── config/              # Configuración de la aplicación

└── main.py              # Punto de entrada de la aplicación

Frontend (React + Vite)

text

frontend/

├── screen/              # Pantallas principales de la aplicación

├── components/          # Componentes reutilizables

├── context/             # Context API para estado global

├── hooks/               # Custom hooks

├── services/api/        # Servicios de comunicación con backend

├── styles/              # Archivos CSS/SCSS

└── App.jsx              # Configuración de rutas principal

🚀 Características Principales

👤 Para Usuarios

Autenticación y Registro: Sistema seguro de login con JWT

Catálogo de Productos: Navegación con filtros y búsqueda

Carrito de Compras: Gestión de productos para compra

Proceso de Checkout: Flujo completo de compra

Historial de Órdenes: Seguimiento de compras anteriores

Sistema de Reseñas: Calificación y comentarios de productos

Gestión de Perfil: Actualización de datos personales

👑 Para Administradores

Dashboard: Métricas y estadísticas del sistema

Gestión de Productos: CRUD completo de productos

Gestión de Órdenes: Administración de pedidos

Gestión de Clientes: Administración de usuarios

Control de Inventario: Actualización de stock

🔧 Tecnologías Utilizadas

Backend
Python 3.11+ - Lenguaje principal
FastAPI - Framework web moderno y rápido
SQLAlchemy - ORM para PostgreSQL
PostgreSQL - Base de datos relacional
JWT - Autenticación por tokens
Pydantic - Validación de datos
Render - Hosting de backend y base de datos
Frontend
React 18 - Biblioteca para interfaces de usuario
React Router - Navegación entre vistas
Context API - Gestión de estado global
React Icons - Biblioteca de iconos
CSS Modules - Estilos modularizados
Vite - Bundler y desarrollo rápido

📁 Estructura de Base de Datos
Principales Entidades
Clientes (clients): Información de usuarios del sistema
Productos (products): Catálogo de productos disponibles
Órdenes (orders): Registro de compras realizadas
Detalles de Orden (order_details): Productos en cada orden
Categorías (categories): Clasificación de productos
Reseñas (reviews): Calificaciones y comentarios
Direcciones (addresses): Direcciones de envío
Facturas (bills): Documentos fiscales

🔐 Sistema de Autenticación
Flujo de Autenticación
Login: Usuario provee credenciales
Validación: Backend verifica en base de datos
Token JWT: Generación de token con datos del usuario
Autorización: Token incluido en cabeceras de peticiones
Middleware: Verificación automática en endpoints protegidos
Roles de Usuario
Administrador (id_key = 0): Acceso completo al sistema
Cliente (id_key > 0): Acceso a funcionalidades básicas

🎯 Funcionalidades por Módulo
Módulo de Productos
Listado paginado de productos
Búsqueda por nombre o categoría
Filtros avanzados
Sistema de calificaciones
Gestión de imágenes
Módulo de Carrito
Agregar/remover productos
Actualizar cantidades
Cálculo automático de totales
Persistencia entre sesiones
Módulo de Órdenes
Creación de nuevas órdenes
Estados: Pendiente → En Proceso → Entregado
Generación automática de facturas
Historial completo de compras
Cancelación de órdenes
Módulo de Administración
Productos: CRUD completo con gestión de stock
Órdenes: Cambio de estados y seguimiento
Clientes: Visualización y eliminación de usuarios
Dashboard: Métricas en tiempo real

🔌 API Endpoints Principales
Autenticación
POST /auth/login - Inicio de sesión
POST /auth/register - Registro de usuario
Productos
GET /products - Lista todos los productos
GET /products/{id} - Obtiene producto específico
POST /products - Crea nuevo producto (admin)
PUT /products/{id} - Actualiza producto (admin)
DELETE /products/{id} - Elimina producto (admin)
Órdenes
GET /orders - Lista órdenes del usuario
POST /orders - Crea nueva orden
GET /orders/{id} - Obtiene detalles de orden
PUT /orders/{id}/status - Cambia estado (admin)
Clientes
GET /clients/me - Perfil del usuario actual
PUT /clients/{id} - Actualiza perfil
GET /clients - Lista todos los clientes (admin)
DELETE /clients/{id} - Elimina cliente (admin)

🎨 Interfaz de Usuario
Pantallas Principales
Login/Registro: Acceso al sistema
Home: Productos destacados y categorías
Catálogo: Lista completa de productos
Detalle de Producto: Información completa con reseñas
Carrito: Resumen de compra
Checkout: Proceso de pago
Perfil: Gestión de cuenta y direcciones
Órdenes: Historial y seguimiento
Admin Dashboard: Panel de administración
Responsive Design
Mobile-first approach
Adaptación a diferentes dispositivos
Experiencia de usuario optimizada

🔒 Seguridad
Medidas Implementadas
HTTPS: Todas las comunicaciones cifradas
JWT Tokens: Autenticación stateless
CORS: Control de acceso entre dominios
Rate Limiting: Protección contra ataques DDoS
Validación de Inputs: Previene inyecciones SQL
Hashing de Passwords: Algoritmo bcrypt
📊 Métricas y Monitoreo
Sistema de Métricas
Usuarios activos
Ventas diarias/semanal
Productos más vendidos
Tasa de conversión
Tiempo promedio de entrega
Health Checks
Monitoreo de servicios
Verificación de base de datos
Estado de caché
Disponibilidad de API

🚀 Despliegue
Backend (Render)
bash

# Variables de entorno necesarias
DATABASE_URL=postgresql://...
SECRET_KEY=your-secret-key
CORS_ORIGINS=["http://localhost:5173"]
Frontend (Netlify/Vercel)
bash

# Build del proyecto
npm run build

# Variables de entorno
VITE_API_URL=https://backend.onrender.com
VITE_ENV=production

📝 Instalación y Configuración Local
Requisitos Previos
Node.js 18+
Python 3.11+
PostgreSQL 14+
npm o yarn
