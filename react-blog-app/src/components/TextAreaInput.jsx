import React from "react";

const TextAreaInput = ({ label, value, setValue, touched, setTouched, minWords, maxWords }) => {
  const words = value.trim().split(/\s+/).filter(Boolean).length;
  const valid = words >= minWords && words <= maxWords;

  return (
    <div>
      <label className="block font-semibold mb-1">{label}</label>
      <textarea
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onBlur={() => setTouched(true)}
        rows={8}
        className={`w-full border rounded px-3 py-2 ${
          touched && !valid ? "border-red-500" : "border-gray-300"
        }`}
      />
      <p className="text-sm text-gray-600 mt-1">
        Word count: {words} (min {minWords}, max {maxWords})
      </p>
    </div>
  );
};

export default TextAreaInput;
