import React, { useState, useEffect } from 'react';

export function ToastModal({ 
  message, 
  type = 'success', 
  isConfirmation = false, 
  onConfirm, 
  onCancel, 
  onClose 
}) {
  const [visible, setVisible] = useState(true);
  const [isClosing, setIsClosing] = useState(false);

  const closeModal = () => {
    setIsClosing(true);
    setTimeout(() => {
      setVisible(false);
      onClose && onClose();
    }, 300);
  };

  useEffect(() => {
    if (!isConfirmation) {
      const timer = setTimeout(() => {
        closeModal();
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [isConfirmation]);

  const handleConfirm = () => {
    closeModal();
    onConfirm && onConfirm();
  };

  const handleCancel = () => {
    closeModal();
    onCancel && onCancel();
  };

  if (!visible) return null;

  const typeStyles = {
    success: 'bg-green-50 border-green-200 text-green-800',
    error: 'bg-red-50 border-red-200 text-red-800',
    warning: 'bg-yellow-50 border-yellow-200 text-yellow-800',
    info: 'bg-blue-50 border-blue-200 text-blue-800'
  };


  return (
    <div className={`fixed top-5 right-5 z-50 max-w-sm w-full shadow-lg rounded-lg border p-4 transition-all duration-300 ${
      isClosing ? 'animate-slide-out-right' : 'animate-slide-in-right'
    } ${typeStyles[type]}`}>
      <div className="flex items-start">

        <div className="flex-1">
          <p className="font-medium text-sm">{message}</p>
          
          {isConfirmation ? (
            <div className="flex justify-end gap-2 mt-4">
  <button
    onClick={handleConfirm}
    className="px-3 py-1.5 bg-red-600 text-white text-xs font-semibold rounded-lg shadow-sm hover:bg-red-700 hover:shadow-md transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500"
  >
    Yes
  </button>
  <button
    onClick={handleCancel}
    className="px-3 py-1.5 bg-gray-200 text-gray-700 text-xs font-semibold rounded-lg shadow-sm hover:bg-gray-300 hover:shadow-md transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-gray-400"
  >
    Cancel
  </button>
</div>

          ) : (
            <button
              onClick={closeModal}
              className="absolute top-2 right-2 text-gray-400 hover:text-gray-600 text-lg leading-none"
            >
              ×
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
