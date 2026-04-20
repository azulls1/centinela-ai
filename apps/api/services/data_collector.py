"""
Servicio para recolección y scraping de datos para entrenamiento
"""

import asyncio
import aiohttp
import os
from typing import List, Dict, Optional
from datetime import datetime
from supabase import Client
import json

class DataCollector:
    """Recolector de datos para entrenamiento de modelos"""
    
    def __init__(self, supabase_client: Client):
        self.supabase = supabase_client
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def scrape_unsplash_images(
        self,
        query: str,
        count: int = 10,
        categories: Optional[List[str]] = None
    ) -> List[Dict]:
        """
        Scrapea imágenes de Unsplash (requiere API key)
        """
        unsplash_api_key = os.getenv("UNSPLASH_ACCESS_KEY")
        if not unsplash_api_key:
            print("⚠️ Unsplash API key no configurada")
            return []
        
        results = []
        url = "https://api.unsplash.com/search/photos"
        
        headers = {
            "Authorization": f"Client-ID {unsplash_api_key}"
        }
        
        params = {
            "query": query,
            "per_page": min(count, 30),
            "page": 1
        }
        
        try:
            async with self.session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    for photo in data.get("results", []):
                        results.append({
                            "source_url": photo["urls"]["full"],
                            "source_platform": "unsplash",
                            "source_type": "image",
                            "tags": [tag["title"] for tag in photo.get("tags", [])],
                            "license": "Unsplash License",
                            "metadata": {
                                "unsplash_id": photo["id"],
                                "description": photo.get("description"),
                                "width": photo["width"],
                                "height": photo["height"],
                                "color": photo.get("color"),
                                "downloads": photo.get("downloads", 0),
                                "likes": photo.get("likes", 0)
                            }
                        })
        except Exception as e:
            print(f"❌ Error scraping Unsplash: {e}")
        
        return results
    
    async def scrape_pexels_images(
        self,
        query: str,
        count: int = 10
    ) -> List[Dict]:
        """
        Scrapea imágenes de Pexels (requiere API key)
        """
        pexels_api_key = os.getenv("PEXELS_API_KEY")
        if not pexels_api_key:
            print("⚠️ Pexels API key no configurada")
            return []
        
        results = []
        url = "https://api.pexels.com/v1/search"
        
        headers = {
            "Authorization": pexels_api_key
        }
        
        params = {
            "query": query,
            "per_page": min(count, 80),
            "page": 1
        }
        
        try:
            async with self.session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    for photo in data.get("photos", []):
                        results.append({
                            "source_url": photo["src"]["large"],
                            "source_platform": "pexels",
                            "source_type": "image",
                            "tags": [query],  # Pexels no proporciona tags directamente
                            "license": "Pexels License",
                            "metadata": {
                                "pexels_id": photo["id"],
                                "photographer": photo["photographer"],
                                "photographer_url": photo["photographer_url"],
                                "width": photo["width"],
                                "height": photo["height"],
                                "color": photo["avg_color"]
                            }
                        })
        except Exception as e:
            print(f"❌ Error scraping Pexels: {e}")
        
        return results
    
    async def download_and_store_image(
        self,
        image_url: str,
        bucket_name: str = "vishum-images",
        file_name: Optional[str] = None
    ) -> Optional[str]:
        """
        Descarga una imagen y la almacena en Supabase Storage
        """
        if not self.session:
            return None
        
        try:
            # Descargar imagen
            async with self.session.get(image_url) as response:
                if response.status == 200:
                    image_data = await response.read()
                    
                    # Generar nombre de archivo si no se proporciona
                    if not file_name:
                        file_name = f"scraped_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(image_url) % 10000}.jpg"
                    
                    # Subir a Supabase Storage
                    storage_response = self.supabase.storage.from_(bucket_name).upload(
                        file_name,
                        image_data,
                        file_options={"content-type": "image/jpeg"}
                    )
                    
                    if storage_response:
                        return f"{bucket_name}/{file_name}"
        except Exception as e:
            print(f"❌ Error descargando imagen: {e}")
        
        return None
    
    async def save_scraped_data(
        self,
        scraped_items: List[Dict],
        dataset_id: Optional[str] = None
    ) -> List[str]:
        """
        Guarda datos scrapeados en la base de datos
        """
        saved_ids = []
        
        for item in scraped_items:
            try:
                # Descargar y almacenar imagen
                file_path = await self.download_and_store_image(item["source_url"])
                
                if file_path:
                    # Guardar en ml_scraped_data
                    scraped_data = {
                        "source_url": item["source_url"],
                        "source_type": item["source_type"],
                        "source_platform": item["source_platform"],
                        "file_path": file_path,
                        "metadata": item.get("metadata", {}),
                        "tags": item.get("tags", []),
                        "license": item.get("license", "unknown"),
                        "is_processed": False
                    }
                    
                    response = self.supabase.table("ml_scraped_data").insert(scraped_data).execute()
                    
                    if response.data:
                        saved_ids.append(response.data[0]["id"])
                        
                        # Si hay dataset_id, crear training_sample
                        if dataset_id:
                            sample_data = {
                                "dataset_id": dataset_id,
                                "file_path": file_path,
                                "file_type": "image",
                                "file_format": "jpg",
                                "metadata": item.get("metadata", {}),
                                "annotation_status": "pending"
                            }
                            
                            self.supabase.table("vishum_ml_training_samples").insert(sample_data).execute()
            except Exception as e:
                print(f"❌ Error guardando dato scrapeado: {e}")
        
        return saved_ids
    
    async def collect_from_events(
        self,
        hours: int = 24,
        min_confidence: float = 0.7
    ) -> int:
        """
        Recolecta imágenes de eventos detectados para entrenamiento
        """
        # Obtener eventos recientes con imágenes
        from_time = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        response = self.supabase.table("vishum_events").select("*").gte("created_at", from_time.isoformat()).execute()
        
        collected_count = 0
        
        for event in response.data:
            payload = event.get("payload", {})
            
            # Verificar si tiene imagen y confianza suficiente
            if payload.get("image_path") and payload.get("confidence", 0) >= min_confidence:
                # Aquí se podría guardar la imagen como training sample
                # Por ahora solo contamos
                collected_count += 1
        
        return collected_count


async def main():
    """
    Función principal para testing
    """
    from supabase_client import get_supabase_client
    
    supabase = get_supabase_client()
    
    async with DataCollector(supabase) as collector:
        # Ejemplo: Scrapear imágenes de personas
        print("🔍 Scrapeando imágenes de Unsplash...")
        unsplash_images = await collector.scrape_unsplash_images("person", count=10)
        print(f"✅ Encontradas {len(unsplash_images)} imágenes")
        
        # Ejemplo: Scrapear imágenes de Pexels
        print("🔍 Scrapeando imágenes de Pexels...")
        pexels_images = await collector.scrape_pexels_images("person", count=10)
        print(f"✅ Encontradas {len(pexels_images)} imágenes")
        
        # Guardar datos scrapeados
        all_images = unsplash_images + pexels_images
        if all_images:
            print(f"💾 Guardando {len(all_images)} imágenes...")
            saved_ids = await collector.save_scraped_data(all_images)
            print(f"✅ Guardadas {len(saved_ids)} imágenes en la base de datos")


if __name__ == "__main__":
    asyncio.run(main())

