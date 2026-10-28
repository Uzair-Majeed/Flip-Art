export const pngDataUrl = (value: string) =>
  value.startsWith('data:') ? value : `data:image/png;base64,${value}`;

export function readImageFile(file: File): Promise<string> {
  if (!/\.(png|jpe?g|bmp|webp)$/i.test(file.name)) {
    return Promise.reject(new Error('Choose a PNG, JPG, BMP, or WebP image.'));
  }
  if (file.size > 10 * 1024 * 1024) {
    return Promise.reject(new Error('Please choose an image smaller than 10 MB.'));
  }
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(String(reader.result));
    reader.onerror = () => reject(new Error('Could not read this file.'));
    reader.readAsDataURL(file);
  });
}
