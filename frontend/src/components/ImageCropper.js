import React, { useState, useRef, useCallback } from 'react';
import ReactCrop from 'react-image-crop';
import 'react-image-crop/dist/ReactCrop.css';
import { X, Check, RotateCcw } from 'lucide-react';

const ImageCropper = ({ imageFile, onCropComplete, onCancel }) => {
  const [crop, setCrop] = useState({
    unit: '%',
    width: 80,
    height: 80,
    x: 10,
    y: 10,
  });
  const [completedCrop, setCompletedCrop] = useState(null);
  const [imageSrc, setImageSrc] = useState('');
  const imgRef = useRef();
  const canvasRef = useRef();

  // Load image when component mounts
  React.useEffect(() => {
    if (imageFile) {
      const reader = new FileReader();
      reader.onload = () => setImageSrc(reader.result);
      reader.readAsDataURL(imageFile);
    }
  }, [imageFile]);

  const onLoad = useCallback((img) => {
    imgRef.current = img;
  }, []);

  const onCropChange = (newCrop) => {
    setCrop(newCrop);
  };

  const onCropCompleteHandler = (newCrop) => {
    setCompletedCrop(newCrop);
  };

  const getCroppedImg = useCallback(() => {
    if (!completedCrop || !imgRef.current) return;

    const canvas = canvasRef.current;
    const image = imgRef.current;
    const ctx = canvas.getContext('2d');

    const scaleX = image.naturalWidth / image.width;
    const scaleY = image.naturalHeight / image.height;

    canvas.width = 400; // Final size 400x400
    canvas.height = 400;

    // Calculate crop dimensions
    const cropX = completedCrop.x * scaleX;
    const cropY = completedCrop.y * scaleY;
    const cropWidth = completedCrop.width * scaleX;
    const cropHeight = completedCrop.height * scaleY;

    ctx.drawImage(
      image,
      cropX,
      cropY,
      cropWidth,
      cropHeight,
      0,
      0,
      400,
      400
    );

    return new Promise((resolve) => {
      canvas.toBlob((blob) => {
        if (blob) {
          const reader = new FileReader();
          reader.onload = () => resolve(reader.result);
          reader.readAsDataURL(blob);
        }
      }, 'image/jpeg', 0.85);
    });
  }, [completedCrop]);

  const handleSave = async () => {
    const croppedImageData = await getCroppedImg();
    if (croppedImageData) {
      onCropComplete(croppedImageData);
    }
  };

  const resetCrop = () => {
    setCrop({
      unit: '%',
      width: 80,
      height: 80,
      x: 10,
      y: 10,
    });
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-[20px] p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-xl font-semibold text-brand-dark">
            Ritaglia la tua foto profilo
          </h3>
          <button
            onClick={onCancel}
            className="text-gray-500 hover:text-gray-700"
          >
            <X size={24} />
          </button>
        </div>

        {/* Instructions */}
        <div className="mb-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <p className="text-blue-800 text-sm">
            📸 <strong>Trascina gli angoli</strong> per ritagliare l'area desiderata. 
            La foto sarà ridimensionata a 400x400px con bordo oro elegante.
          </p>
        </div>

        {/* Crop Area */}
        {imageSrc && (
          <div className="mb-6 flex justify-center">
            <ReactCrop
              crop={crop}
              onChange={onCropChange}
              onComplete={onCropCompleteHandler}
              aspect={1} // Square crop
              minWidth={50}
              minHeight={50}
              className="max-w-full max-h-96"
            >
              <img
                ref={imgRef}
                alt="Crop"
                src={imageSrc}
                onLoad={onLoad}
                className="max-w-full max-h-96 object-contain"
              />
            </ReactCrop>
          </div>
        )}

        {/* Preview */}
        {completedCrop && (
          <div className="mb-6 text-center">
            <h4 className="text-sm font-medium text-brand-dark mb-3">Anteprima:</h4>
            <div className="inline-block">
              <div className="w-24 h-24 rounded-full overflow-hidden avatar-ring mx-auto">
                <canvas
                  ref={canvasRef}
                  className="w-full h-full object-cover"
                  style={{ display: 'none' }}
                />
                <div 
                  id="preview"
                  className="w-full h-full bg-gray-200 flex items-center justify-center text-gray-500 text-xs"
                >
                  Preview
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Actions */}
        <div className="flex space-x-3 justify-end">
          <button
            onClick={resetCrop}
            className="flex items-center space-x-2 px-4 py-2 border border-gray-300 text-gray-700 rounded-[12px] hover:bg-gray-50 transition-colors"
          >
            <RotateCcw size={16} />
            <span>Reset</span>
          </button>
          
          <button
            onClick={onCancel}
            className="px-6 py-2 border border-gray-300 text-gray-700 rounded-[12px] hover:bg-gray-50 transition-colors"
          >
            Annulla
          </button>
          
          <button
            onClick={handleSave}
            className="flex items-center space-x-2 px-6 py-2 bg-brand-accent hover:bg-opacity-90 text-white rounded-[12px] transition-colors"
            disabled={!completedCrop}
          >
            <Check size={16} />
            <span>Salva Foto</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default ImageCropper;