import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
)
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
import httpx

import os
from dotenv import load_dotenv


load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

def weather_by_coords(lat: float, lon: float) -> list:
    API_URL = "http://api.weatherstack.com/current"
    params = {
        "access_key": WEATHER_API_KEY,
        "query": f"{lat},{lon}",
    }
    
    response = httpx.get(API_URL, params=params)
    data = response.json()
    
    location = data["location"]["name"]
    country = data["location"]["country"]
    temperature = data["current"]["temperature"]
    description = data["current"]["weather_descriptions"]
    wind_speed = data["current"]["wind_speed"]
    visibility = data["current"]["visibility"]

    return [
        [f"Location: {location}, {country}"],
        [f"Temperature: {temperature}°C"],
        [f"{description[0]}"],
        [f"WindSpeed: {wind_speed}"],
        [f"Visibility: {visibility}"]
    ]

geo_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📍 Send location", request_location=True)]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

def refresh_button(lat, lon):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Refresh", callback_data=f"refresh:{lat}:{lon}")]
    ])

@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer("Hi! Send me your location so i can show you your weather ☀️", reply_markup=geo_keyboard)

@dp.message(F.location)
async def handle_location(message: types.Message):
    lat = message.location.latitude
    lon = message.location.longitude

    try:
        weather_data = weather_by_coords(lat, lon)
        text = "\n".join([line[0] for line in weather_data])
        await message.answer(
            text,
            parse_mode=ParseMode.HTML,
            reply_markup=refresh_button(lat, lon)
        )
    except Exception:
        await message.answer("Something went wrong 😞")

@dp.callback_query(F.data.startswith("refresh:"))
async def refresh_weather(callback: types.CallbackQuery):
    _, lat, lon = callback.data.split(":")
    try:
        weather_data = weather_by_coords(float(lat), float(lon))
        text = "\n".join([line[0] for line in weather_data])
        await callback.message.edit_text(text, reply_markup=refresh_button(lat, lon))
    except Exception:
        await callback.message.answer("Unexcpected problem while reloading 😓")
    await callback.answer()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
