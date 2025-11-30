import { useState, useRef, useEffect } from 'react';

const SearchableDropdown = ({
  label,
  options = [],
  selectedValues = [],
  onChange,
  placeholder = 'Select...',
  searchPlaceholder = 'Search...'
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const dropdownRef = useRef(null);
  const searchInputRef = useRef(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
        setSearchTerm('');
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Focus search input when dropdown opens
  useEffect(() => {
    if (isOpen && searchInputRef.current) {
      searchInputRef.current.focus();
    }
  }, [isOpen]);

  const filteredOptions = options.filter(option =>
    option.toString().toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleToggle = (value) => {
    const newValues = selectedValues.includes(value)
      ? selectedValues.filter(v => v !== value)
      : [...selectedValues, value];
    onChange(newValues);
  };

  const handleClearAll = (e) => {
    e.stopPropagation();
    onChange([]);
  };

  const getDisplayText = () => {
    if (selectedValues.length === 0) return placeholder;
    if (selectedValues.length === 1) return selectedValues[0];
    return `${selectedValues.length} selected`;
  };

  return (
    <div className="searchable-dropdown" ref={dropdownRef}>
      {label && <label className="dropdown-label">{label}</label>}

      <button
        type="button"
        className={`dropdown-trigger ${isOpen ? 'open' : ''} ${selectedValues.length > 0 ? 'has-value' : ''}`}
        onClick={() => setIsOpen(!isOpen)}
      >
        <span className="dropdown-trigger-text">{getDisplayText()}</span>
        <div className="dropdown-trigger-icons">
          {selectedValues.length > 0 && (
            <span className="clear-btn" onClick={handleClearAll} title="Clear all">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <line x1="18" y1="6" x2="6" y2="18"></line>
                <line x1="6" y1="6" x2="18" y2="18"></line>
              </svg>
            </span>
          )}
          <svg
            className={`chevron ${isOpen ? 'rotate' : ''}`}
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
          >
            <polyline points="6 9 12 15 18 9"></polyline>
          </svg>
        </div>
      </button>

      {isOpen && (
        <div className="dropdown-menu">
          <div className="dropdown-search-container">
            <svg className="search-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="11" cy="11" r="8"></circle>
              <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
            </svg>
            <input
              ref={searchInputRef}
              type="text"
              className="dropdown-search"
              placeholder={searchPlaceholder}
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              onClick={(e) => e.stopPropagation()}
            />
          </div>

          <div className="dropdown-options">
            {filteredOptions.length === 0 ? (
              <div className="dropdown-no-results">No results found</div>
            ) : (
              filteredOptions.map((option) => (
                <label key={option} className="dropdown-option">
                  <input
                    type="checkbox"
                    checked={selectedValues.includes(option)}
                    onChange={() => handleToggle(option)}
                  />
                  <span className="checkbox-custom"></span>
                  <span className="option-text">{option}</span>
                </label>
              ))
            )}
          </div>

          {selectedValues.length > 0 && (
            <div className="dropdown-footer">
              <span className="selected-count">{selectedValues.length} selected</span>
              <button type="button" className="clear-all-btn" onClick={handleClearAll}>
                Clear all
              </button>
            </div>
          )}
        </div>
      )}

      <style jsx>{`
        .searchable-dropdown {
          position: relative;
          width: 100%;
          font-family: 'Inter', sans-serif;
        }

        .dropdown-label {
          display: block;
          font-size: 12px;
          font-weight: 500;
          letter-spacing: 0.1em;
          text-transform: uppercase;
          color: #C4BFC0;
          margin-bottom: 10px;
        }

        .dropdown-trigger {
          width: 100%;
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 8px;
          padding: 10px 14px;
          background: rgba(255, 255, 255, 0.03);
          border: 1px solid rgba(196, 191, 192, 0.2);
          border-radius: 4px;
          color: rgba(196, 191, 192, 0.5);
          font-family: 'Inter', sans-serif;
          font-size: 13px;
          cursor: pointer;
          transition: all 0.3s ease;
          text-align: left;
        }

        .dropdown-trigger:hover {
          border-color: rgba(196, 191, 192, 0.4);
        }

        .dropdown-trigger.open {
          border-color: #4075C9;
          background: rgba(64, 117, 201, 0.05);
          box-shadow: 0 0 0 3px rgba(64, 117, 201, 0.1);
        }

        .dropdown-trigger.has-value {
          color: #ffffff;
        }

        .dropdown-trigger-text {
          flex: 1;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }

        .dropdown-trigger-icons {
          display: flex;
          align-items: center;
          gap: 4px;
        }

        .clear-btn {
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 2px;
          border-radius: 4px;
          opacity: 0.6;
          transition: all 0.2s ease;
        }

        .clear-btn:hover {
          opacity: 1;
          background: rgba(255, 255, 255, 0.1);
        }

        .chevron {
          opacity: 0.6;
          transition: transform 0.2s ease;
        }

        .chevron.rotate {
          transform: rotate(180deg);
        }

        .dropdown-menu {
          position: absolute;
          top: calc(100% + 4px);
          left: 0;
          right: 0;
          background: rgba(10, 10, 18, 0.98);
          backdrop-filter: blur(20px);
          border: 1px solid rgba(64, 117, 201, 0.2);
          border-radius: 4px;
          box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
          z-index: 100;
          animation: dropdownSlideIn 0.15s ease-out;
          overflow: hidden;
        }

        @keyframes dropdownSlideIn {
          from {
            opacity: 0;
            transform: translateY(-8px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        .dropdown-search-container {
          position: relative;
          padding: 10px;
          border-bottom: 1px solid rgba(64, 117, 201, 0.15);
        }

        .search-icon {
          position: absolute;
          left: 20px;
          top: 50%;
          transform: translateY(-50%);
          opacity: 0.5;
        }

        .dropdown-search {
          width: 100%;
          padding: 8px 12px 8px 36px;
          background: rgba(255, 255, 255, 0.03);
          border: 1px solid rgba(196, 191, 192, 0.2);
          border-radius: 4px;
          color: #ffffff;
          font-family: 'Inter', sans-serif;
          font-size: 12px;
          outline: none;
          transition: all 0.3s ease;
        }

        .dropdown-search:focus {
          border-color: #4075C9;
          background: rgba(64, 117, 201, 0.05);
        }

        .dropdown-search::placeholder {
          color: rgba(196, 191, 192, 0.5);
        }

        .dropdown-options {
          max-height: 180px;
          overflow-y: auto;
          padding: 4px 0;
        }

        .dropdown-options::-webkit-scrollbar {
          width: 6px;
        }

        .dropdown-options::-webkit-scrollbar-track {
          background: transparent;
        }

        .dropdown-options::-webkit-scrollbar-thumb {
          background: rgba(64, 117, 201, 0.4);
          border-radius: 3px;
        }

        .dropdown-options::-webkit-scrollbar-thumb:hover {
          background: rgba(64, 117, 201, 0.6);
        }

        .dropdown-option {
          display: flex;
          align-items: center;
          gap: 10px;
          padding: 8px 14px;
          cursor: pointer;
          transition: background 0.15s ease;
        }

        .dropdown-option:hover {
          background: rgba(64, 117, 201, 0.1);
        }

        .dropdown-option input[type="checkbox"] {
          display: none;
        }

        .checkbox-custom {
          width: 14px;
          height: 14px;
          border: 1px solid rgba(196, 191, 192, 0.4);
          border-radius: 3px;
          display: flex;
          align-items: center;
          justify-content: center;
          transition: all 0.2s ease;
          flex-shrink: 0;
        }

        .dropdown-option input[type="checkbox"]:checked + .checkbox-custom {
          background: #4075C9;
          border-color: #4075C9;
        }

        .dropdown-option input[type="checkbox"]:checked + .checkbox-custom::after {
          content: '';
          width: 3px;
          height: 6px;
          border: solid white;
          border-width: 0 1.5px 1.5px 0;
          transform: rotate(45deg);
          margin-bottom: 1px;
        }

        .option-text {
          font-family: 'Inter', sans-serif;
          font-size: 12px;
          color: #C4BFC0;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }

        .dropdown-option:hover .option-text {
          color: #ffffff;
        }

        .dropdown-no-results {
          padding: 16px;
          text-align: center;
          color: #C4BFC0;
          font-family: 'Inter', sans-serif;
          font-size: 12px;
        }

        .dropdown-footer {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 10px 14px;
          border-top: 1px solid rgba(64, 117, 201, 0.15);
          background: rgba(0, 0, 0, 0.2);
        }

        .selected-count {
          font-family: 'Inter', sans-serif;
          font-size: 11px;
          color: #C4BFC0;
        }

        .clear-all-btn {
          background: transparent;
          border: none;
          color: #4075C9;
          font-family: 'Inter', sans-serif;
          font-size: 11px;
          font-weight: 500;
          cursor: pointer;
          padding: 4px 8px;
          border-radius: 4px;
          transition: all 0.2s ease;
        }

        .clear-all-btn:hover {
          background: rgba(64, 117, 201, 0.15);
        }
      `}</style>
    </div>
  );
};

export default SearchableDropdown;
