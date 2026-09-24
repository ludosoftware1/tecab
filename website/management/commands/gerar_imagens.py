"""Gera as variantes responsivas (WebP) das imagens do catálogo `website/images.py`."""
import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from PIL import Image, ImageOps

from website.images import IMAGES

STATIC_IMG = Path(settings.BASE_DIR) / 'website' / 'static' / 'img'


def _crop(im, ratio):
    w, h = im.size
    if w / h > ratio:  # largo demais: corta nas laterais
        nw = round(h * ratio)
        left = (w - nw) // 2
        return im.crop((left, 0, left + nw, h))
    nh = round(w / ratio)
    top = (h - nh) // 2
    return im.crop((0, top, w, top + nh))


class Command(BaseCommand):
    help = 'Gera imagens WebP responsivas em website/static/img a partir dos originais em assets_src/.'

    def add_arguments(self, parser):
        parser.add_argument('--origem', default=str(Path(settings.BASE_DIR) / 'assets_src'))
        parser.add_argument('--apenas', nargs='*', help='Gerar somente estas chaves')
        parser.add_argument('--extras', action='store_true', help='Gerar também favicons e imagem de compartilhamento')

    def handle(self, *args, origem, apenas, extras, **opts):
        origem = Path(origem)
        if not origem.is_dir():
            raise CommandError('Pasta de origem não encontrada: %s' % origem)
        STATIC_IMG.mkdir(parents=True, exist_ok=True)
        manifest_path = STATIC_IMG / 'manifest.json'
        manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}

        for key, (src, widths, ratio, trim) in IMAGES.items():
            if apenas and key not in apenas:
                continue
            im = ImageOps.exif_transpose(Image.open(origem / src))
            im = im.convert('RGBA') if im.mode in ('RGBA', 'LA', 'P') else im.convert('RGB')
            if trim and im.mode == 'RGBA':
                im = im.crop(im.getchannel('A').getbbox())
            if ratio:
                im = _crop(im, ratio)
            usable = [w for w in widths if w <= im.width] or [im.width]
            for w in usable:
                h = round(im.height * w / im.width)
                im.resize((w, h), Image.LANCZOS).save(STATIC_IMG / ('%s-%d.webp' % (key, w)), 'WEBP',
                                                      quality=80, method=6)
            manifest[key] = {'widths': usable, 'width': usable[-1], 'height': round(im.height * usable[-1] / im.width)}
            self.stdout.write('%s: %s' % (key, usable))

        manifest_path.write_text(json.dumps(manifest, indent=1, sort_keys=True))
        if extras:
            self._extras(origem)
        self.stdout.write(self.style.SUCCESS('Manifesto atualizado: %s' % manifest_path))

    def _extras(self, origem):
        # Imagem para compartilhamento (Open Graph) 1200x630
        hero = ImageOps.exif_transpose(Image.open(origem / IMAGES['terminal-aereo-rio'][0])).convert('RGB')
        _crop(hero, 1200 / 630).resize((1200, 630), Image.LANCZOS).save(STATIC_IMG / 'og-tecab.jpg', quality=82)
        # Favicons: ícone da gota (parte superior do logotipo) sobre fundo transparente
        logo = Image.open(origem / 'marca/logo.png').convert('RGBA')
        logo = logo.crop(logo.getchannel('A').getbbox())
        icon = logo.crop((0, 0, logo.width, round(logo.height * 0.62)))
        icon = icon.crop(icon.getchannel('A').getbbox())
        side = max(icon.size)
        square = Image.new('RGBA', (side, side), (0, 0, 0, 0))
        square.paste(icon, ((side - icon.width) // 2, (side - icon.height) // 2))
        for size, name in ((32, 'favicon-32.png'), (192, 'icon-192.png'), (512, 'icon-512.png')):
            square.resize((size, size), Image.LANCZOS).save(STATIC_IMG / name)
        # apple-touch-icon com fundo branco e margem
        touch = Image.new('RGBA', (180, 180), (255, 255, 255, 255))
        small = square.resize((132, 132), Image.LANCZOS)
        touch.alpha_composite(small, (24, 24))
        touch.convert('RGB').save(STATIC_IMG / 'apple-touch-icon.png')
        self.stdout.write('favicons e og-tecab.jpg gerados')
