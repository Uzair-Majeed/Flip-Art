export type ImageKind = 'photo' | 'sketch';
export type ConversionMode = 'auto' | ImageKind;
export type InputTab = 'upload' | 'camera';
export type BackendStatus = 'Connecting' | 'Models ready' | 'Backend unavailable';

export interface ConversionOptions {
  face_crop: boolean;
  grayscale_sketch: boolean;
  enhance_contrast: boolean;
  clean_sketch: boolean;
}

export interface ConversionRequest extends ConversionOptions {
  image: string;
  mode: ConversionMode;
}

export interface ImagePreview {
  detected_type: ImageKind;
  effective_input_type: ImageKind;
  direction: 'photo->sketch' | 'sketch->photo';
  detection_confidence: number;
  face_found: boolean | null;
  input_preview: string;
  cleanup_applied: boolean;
  manual_override: boolean;
}

export interface ConversionResult extends ImagePreview {
  output_image: string;
  inference_ms: number;
}
