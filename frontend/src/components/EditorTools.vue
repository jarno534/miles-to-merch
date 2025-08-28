<template>
  <div class="editor-tools-sidebar">
    <h2>Tools</h2>
    <div class="tools-section">
      <button @click="$emit('save-design')" class="tool-button save-button">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 24 24"
          fill="currentColor"
        >
          <path
            d="M17 3H5c-1.11 0-2 .9-2 2v14c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V7l-4-4zm-5 16c-1.66 0-3-1.34-3-3s1.34-3 3-3 3 1.34 3 3-1.34 3-3 3zm3-10H5V5h10v4z"
          />
        </svg>
        Save Design
      </button>
    </div>
    <div class="tools-section">
      <button
        @click="$emit('clear-canvas')"
        class="tool-button clear-all-button"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 24 24"
          fill="currentColor"
        >
          <path
            d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"
          />
        </svg>
        <span>Clear Canvas</span>
      </button>
    </div>
    <div class="tools-section">
      <p class="category-title">History</p>
      <div class="button-grid-tools">
        <button @click="$emit('undo')" :disabled="!canUndo" class="tool-button">
          <svg viewBox="0 0 24 24" fill="currentColor">
            <path
              d="M12.5 8c-2.65 0-5.05.99-6.9 2.6L2 7v9h9l-3.62-3.62c1.39-1.16 3.16-1.88 5.12-1.88 3.54 0 6.55 2.31 7.6 5.5l2.37-.78C21.08 11.03 17.15 8 12.5 8z"
            />
          </svg>
          Undo
        </button>
        <button @click="$emit('redo')" :disabled="!canRedo" class="tool-button">
          <svg viewBox="0 0 24 24" fill="currentColor">
            <path
              d="M18.4 10.6C16.55 8.99 14.15 8 11.5 8c-4.65 0-8.58 3.03-9.96 7.22L3.9 16c1.05-3.19 4.05-5.5 7.6-5.5 1.96 0 3.73.72 5.12 1.88L13 16h9V7l-3.6 3.6z"
            />
          </svg>
          Redo
        </button>
      </div>
    </div>
    <div v-if="selection.type" class="tools-section">
      <p class="category-title">Clipboard</p>
      <div class="button-grid-tools">
        <button
          @click="$emit('cut')"
          :disabled="!canCopyCutDelete"
          class="tool-button"
        >
          <svg
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <circle cx="6" cy="6" r="3"></circle>
            <circle cx="6" cy="18" r="3"></circle>
            <line x1="20" y1="4" x2="8.12" y2="15.88"></line>
            <line x1="14.47" y1="14.48" x2="20" y2="20"></line>
            <line x1="8.12" y1="8.12" x2="12" y2="12"></line>
          </svg>
          Cut
        </button>
        <button
          @click="$emit('copy')"
          :disabled="!canCopyCutDelete"
          class="tool-button"
        >
          <svg viewBox="0 0 24 24" fill="currentColor">
            <path
              d="M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z"
            />
          </svg>
          Copy
        </button>
        <button
          @click="$emit('paste')"
          :disabled="!canPaste"
          class="tool-button"
        >
          <svg viewBox="0 0 24 24" fill="currentColor">
            <path
              d="M19 2h-4.18C14.4.84 13.3 0 12 0S9.6.84 9.18 2H5c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-7 0c.55 0 1 .45 1 1s-.45 1-1 1-1-.45-1-1 .45-1 1-1zm7 18H5V4h2v3h10V4h2v16z"
            />
          </svg>
          Paste
        </button>
      </div>
    </div>
    <div v-if="selection.type" class="tools-section">
      <p class="category-title">Actions</p>
      <div class="button-grid-tools">
        <button
          @click="$emit('delete-selected')"
          :disabled="!canCopyCutDelete"
          class="tool-button"
        >
          Delete
        </button>
        <button @click="$emit('deselect-all')" class="tool-button">
          Deselect
        </button>
      </div>
    </div>
    <div v-if="selection.type" class="tools-section">
      <p class="category-title">Alignment</p>
      <div class="button-grid-tools align-grid">
        <button
          @click="$emit('align-element', 'left')"
          class="tool-button"
          title="Align Left"
        >
          <svg viewBox="0 0 20 20" fill="currentColor">
            <rect x="1" y="1" width="3" height="18"></rect>
            <rect x="6" y="5" width="8" height="4"></rect>
            <rect x="6" y="11" width="12" height="4"></rect>
          </svg>
        </button>
        <button
          @click="$emit('align-element', 'center-h')"
          class="tool-button"
          title="Align Center Horizontally"
        >
          <svg viewBox="0 0 20 20" fill="currentColor">
            <rect x="8.5" y="1" width="3" height="18"></rect>
            <rect x="4" y="5" width="12" height="4"></rect>
            <rect x="2" y="11" width="16" height="4"></rect>
          </svg>
        </button>
        <button
          @click="$emit('align-element', 'right')"
          class="tool-button"
          title="Align Right"
        >
          <svg viewBox="0 0 20 20" fill="currentColor">
            <rect x="16" y="1" width="3" height="18"></rect>
            <rect x="6" y="5" width="8" height="4"></rect>
            <rect x="2" y="11" width="12" height="4"></rect>
          </svg>
        </button>
        <button
          @click="$emit('align-element', 'top')"
          class="tool-button"
          title="Align Top"
        >
          <svg viewBox="0 0 20 20" fill="currentColor">
            <rect x="1" y="1" width="18" height="3"></rect>
            <rect x="6" y="6" width="4" height="8"></rect>
            <rect x="12" y="6" width="4" height="12"></rect>
          </svg>
        </button>
        <button
          @click="$emit('align-element', 'center-v')"
          class="tool-button"
          title="Align Center Vertically"
        >
          <svg viewBox="0 0 20 20" fill="currentColor">
            <rect x="1" y="8.5" width="18" height="3"></rect>
            <rect x="5" y="4" width="4" height="12"></rect>
            <rect x="11" y="2" width="4" height="16"></rect>
          </svg>
        </button>
        <button
          @click="$emit('align-element', 'bottom')"
          class="tool-button"
          title="Align Bottom"
        >
          <svg viewBox="0 0 20 20" fill="currentColor">
            <rect x="1" y="16" width="18" height="3"></rect>
            <rect x="6" y="6" width="4" height="8"></rect>
            <rect x="12" y="2" width="4" height="12"></rect>
          </svg>
        </button>
      </div>
    </div>
    <div v-if="selection.type" class="tools-section">
      <p class="category-title">Order</p>
      <div class="button-grid-tools layer-grid">
        <button
          @click="$emit('bring-forward')"
          class="tool-button"
          title="Bring Forward"
        >
          <svg
            version="1.0"
            xmlns="http://www.w3.org/2000/svg"
            width="24"
            height="24"
            viewBox="0 0 354 321"
            preserveAspectRatio="xMidYMid meet"
          >
            <g transform="translate(0,321) scale(0.1,-0.1)" fill="currentColor">
              <path
                d="M1700 2816 c-25 -7 -104 -79 -289 -262 l-255 -252 0 -51 c0 -39 5 -56 23 -75 26 -27 73 -39 113 -28 17 4 96 75 196 175 137 135 171 165 180 154 9 -10 12 -184 12 -634 -1 -462 2 -627 11 -647 16 -34 68 -66 105 -66 32 1 75 32 93 67 8 16 11 195 11 648 0 510 3 627 14 631 7 3 81 -63 178 -160 119 -117 175 -166 197 -171 101 -22 169 66 121 157 -21 41 -391 418 -464 473 -65 50 -165 66 -246 41z"
              />
              <path
                d="M1095 1688 c-121 -61 -249 -124 -285 -140 -36 -17 -72 -35 -80 -39 -8 -5 -22 -12 -30 -15 -8 -3 -22 -10 -30 -15 -8 -5 -22 -12 -30 -15 -8 -3 -22 -10 -30 -15 -8 -5 -22 -12 -30 -15 -52 -21 -192 -96 -207 -111 -43 -44 -54 -105 -28 -166 17 -42 42 -60 155 -116 47 -23 92 -46 100 -51 8 -5 74 -37 145 -70 72 -34 240 -116 375 -182 304 -150 473 -231 526 -253 57 -23 241 -24 290 -1 19 9 51 23 72 32 20 9 44 20 52 25 8 5 22 12 30 15 8 3 22 10 30 15 8 5 22 12 30 15 8 3 22 10 30 15 8 5 22 12 30 15 31 13 207 99 590 289 372 184 398 198 423 237 45 69 30 141 -39 194 -34 26 -166 94 -274 141 -19 8 -42 19 -50 24 -8 5 -21 11 -27 14 -7 3 -19 7 -25 10 -7 3 -21 9 -30 15 -34 19 -53 29 -98 50 -25 12 -52 26 -60 31 -8 5 -22 12 -30 15 -8 3 -22 10 -30 15 -8 5 -22 12 -30 15 -8 3 -22 10 -30 15 -8 5 -22 12 -30 15 -8 3 -59 27 -114 55 -54 27 -102 46 -107 43 -5 -3 -9 -56 -9 -119 l0 -113 198 -97 c108 -54 204 -101 212 -106 8 -5 22 -12 30 -15 8 -3 22 -10 30 -15 8 -5 22 -12 30 -15 8 -3 22 -10 30 -15 8 -5 22 -12 30 -15 120 -50 128 -69 43 -110 -66 -30 -798 -390 -886 -435 -32 -16 -85 -36 -118 -43 -51 -12 -66 -12 -111 1 -29 8 -60 19 -68 24 -8 5 -22 12 -30 15 -8 3 -22 9 -30 14 -8 5 -35 19 -60 30 -25 12 -52 26 -60 31 -8 5 -22 12 -30 15 -8 3 -22 10 -30 15 -8 5 -21 11 -27 14 -7 3 -19 7 -25 10 -7 3 -20 9 -28 14 -8 5 -76 38 -150 74 -408 196 -510 250 -510 267 0 18 20 29 250 137 52 24 102 49 110 54 8 5 22 12 30 15 8 3 22 10 30 15 8 5 22 12 30 15 15 6 119 55 178 83 l33 16 -3 119 c-2 69 -7 120 -13 121 -5 1 -109 -47 -230 -107z"
              />
            </g>
          </svg>
          Forward
        </button>
        <button
          @click="$emit('send-backward')"
          class="tool-button"
          title="Send Backward"
        >
          <svg
            width="24"
            height="24"
            viewBox="0 0 354 321"
            preserveAspectRatio="xMidYMid meet"
          >
            <g transform="rotate(180, 177, 160.5)">
              <g
                transform="translate(0,321) scale(0.1,-0.1)"
                fill="currentColor"
              >
                <path
                  d="M1700 2816 c-25 -7 -104 -79 -289 -262 l-255 -252 0 -51 c0 -39 5 -56 23 -75 26 -27 73 -39 113 -28 17 4 96 75 196 175 137 135 171 165 180 154 9 -10 12 -184 12 -634 -1 -462 2 -627 11 -647 16 -34 68 -66 105 -66 32 1 75 32 93 67 8 16 11 195 11 648 0 510 3 627 14 631 7 3 81 -63 178 -160 119 -117 175 -166 197 -171 101 -22 169 66 121 157 -21 41 -391 418 -464 473 -65 50 -165 66 -246 41z"
                />
                <path
                  d="M1095 1688 c-121 -61 -249 -124 -285 -140 -36 -17 -72 -35 -80 -39 -8 -5 -22 -12 -30 -15 -8 -3 -22 -10 -30 -15 -8 -5 -22 -12 -30 -15 -8 -3 -22 -10 -30 -15 -8 -5 -22 -12 -30 -15 -52 -21 -192 -96 -207 -111 -43 -44 -54 -105 -28 -166 17 -42 42 -60 155 -116 47 -23 92 -46 100 -51 8 -5 74 -37 145 -70 72 -34 240 -116 375 -182 304 -150 473 -231 526 -253 57 -23 241 -24 290 -1 19 9 51 23 72 32 20 9 44 20 52 25 8 5 22 12 30 15 8 3 22 10 30 15 8 5 22 12 30 15 8 3 22 10 30 15 8 5 22 12 30 15 31 13 207 99 590 289 372 184 398 198 423 237 45 69 30 141 -39 194 -34 26 -166 94 -274 141 -19 8 -42 19 -50 24 -8 5 -21 11 -27 14 -7 3 -19 7 -25 10 -7 3 -21 9 -30 15 -34 19 -53 29 -98 50 -25 12 -52 26 -60 31 -8 5 -22 12 -30 15 -8 3 -22 10 -30 15 -8 5 -22 12 -30 15 -8 3 -22 10 -30 15 -8 5 -22 12 -30 15 -8 3 -59 27 -114 55 -54 27 -102 46 -107 43 -5 -3 -9 -56 -9 -119 l0 -113 198 -97 c108 -54 204 -101 212 -106 8 -5 22 -12 30 -15 8 -3 22 -10 30 -15 8 -5 22 -12 30 -15 8 -3 22 -10 30 -15 8 -5 22 -12 30 -15 120 -50 128 -69 43 -110 -66 -30 -798 -390 -886 -435 -32 -16 -85 -36 -118 -43 -51 -12 -66 -12 -111 1 -29 8 -60 19 -68 24 -8 5 -22 12 -30 15 -8 3 -22 9 -30 14 -8 5 -35 19 -60 30 -25 12 -52 26 -60 31 -8 5 -22 12 -30 15 -8 3 -22 10 -30 15 -8 5 -21 11 -27 14 -7 3 -19 7 -25 10 -7 3 -20 9 -28 14 -8 5 -76 38 -150 74 -408 196 -510 250 -510 267 0 18 20 29 250 137 52 24 102 49 110 54 8 5 22 12 30 15 8 3 22 10 30 15 8 5 22 12 30 15 15 6 119 55 178 83 l33 16 -3 119 c-2 69 -7 120 -13 121 -5 1 -109 -47 -230 -107z"
                />
              </g>
            </g>
          </svg>
          Backward
        </button>
        <button
          @click="$emit('bring-to-front')"
          class="tool-button"
          title="Bring to Front"
        >
          <svg
            version="1.0"
            xmlns="http://www.w3.org/2000/svg"
            width="24"
            height="24"
            viewBox="0 0 402 390"
            preserveAspectRatio="xMidYMid meet"
          >
            <g transform="translate(0,390) scale(0.1,-0.1)" fill="currentColor">
              <path
                d="M1890 3507 c-41 -10 -70 -36 -300 -264 l-255 -252 2 -52 c2 -72 32 -103 103 -103 l51 0 175 175 c139 139 176 171 184 159 6 -9 10 -283 10 -706 0 -756 -1 -738 59 -775 40 -24 68 -24 105 0 57 38 55 9 56 769 0 600 2 703 14 708 9 4 68 -48 163 -144 81 -82 167 -160 190 -171 74 -39 143 -8 157 70 4 20 2 48 -4 63 -10 27 -408 432 -470 478 -70 53 -145 67 -240 45z"
              />
              <path
                d="M2424 2477 c-2 -7 -3 -62 -2 -121 l3 -108 65 -33 c36 -18 117 -57 180 -88 63 -31 175 -85 248 -121 74 -36 140 -66 147 -66 16 0 26 -25 19 -45 -4 -8 -14 -15 -23 -15 -10 0 -26 -7 -37 -15 -10 -8 -26 -15 -35 -15 -9 0 -22 -7 -29 -15 -7 -8 -20 -15 -30 -15 -10 0 -23 -7 -30 -15 -7 -8 -20 -15 -30 -15 -10 0 -23 -7 -30 -15 -7 -8 -20 -15 -30 -15 -10 0 -23 -7 -30 -15 -7 -8 -19 -15 -26 -15 -7 0 -159 -72 -336 -161 -178 -88 -351 -169 -385 -180 -62 -20 -64 -20 -125 0 -35 10 -263 118 -507 240 -244 122 -450 221 -456 221 -7 0 -18 6 -25 14 -6 8 -21 16 -33 18 -33 5 -30 49 3 59 14 4 161 75 328 158 l302 151 0 115 c0 114 0 115 -24 115 -13 0 -29 -7 -36 -15 -7 -8 -19 -15 -27 -15 -24 0 -867 -424 -885 -445 -32 -39 -42 -89 -27 -141 15 -51 43 -77 119 -112 105 -48 144 -67 188 -92 9 -6 24 -13 32 -16 8 -3 22 -10 30 -15 8 -5 22 -12 30 -15 8 -3 205 -100 436 -215 232 -115 429 -209 438 -209 9 0 28 -7 41 -16 38 -25 203 -22 282 5 49 16 853 406 913 442 8 5 22 12 30 15 8 3 56 25 105 50 50 24 95 44 101 44 7 0 17 7 24 15 7 8 20 15 30 15 26 0 85 65 100 110 16 47 1 106 -34 139 -18 17 -937 481 -952 481 -3 0 -7 -6 -10 -13z"
              />
              <path
                d="M2976 1341 c-60 -31 -111 -62 -113 -68 -2 -5 48 -36 112 -67 65 -32 115 -63 113 -69 -2 -7 -139 -79 -304 -161 -164 -81 -306 -152 -314 -157 -8 -5 -22 -12 -30 -15 -8 -3 -22 -10 -30 -15 -8 -5 -22 -12 -30 -15 -8 -3 -22 -10 -30 -15 -8 -5 -22 -12 -30 -15 -23 -9 -203 -95 -220 -105 -38 -23 -119 -39 -147 -28 -14 5 -35 9 -48 9 -20 0 -54 13 -105 42 -8 4 -22 11 -30 14 -8 3 -22 10 -30 15 -8 5 -22 12 -30 15 -8 3 -22 10 -30 15 -8 5 -22 12 -30 15 -20 8 -197 94 -520 252 -146 72 -272 137 -279 146 -11 13 -8 17 21 29 112 48 206 100 202 110 -5 14 -207 117 -229 117 -21 0 -229 -104 -270 -136 -59 -45 -79 -110 -53 -171 26 -60 36 -66 413 -248 99 -48 239 -115 310 -150 72 -35 150 -73 175 -85 25 -11 52 -25 60 -30 8 -5 35 -18 60 -30 25 -11 52 -25 60 -29 34 -19 197 -96 230 -109 19 -7 70 -16 112 -19 96 -7 144 6 318 89 69 33 168 80 220 105 52 25 102 49 110 54 8 5 22 12 30 15 8 3 22 10 30 15 8 5 22 12 30 15 8 3 22 10 30 15 8 5 22 12 30 15 61 24 629 310 646 325 51 48 55 143 7 199 -22 27 -264 161 -298 166 -5 1 -59 -24 -119 -55z"
              />
            </g>
          </svg>
          To Front
        </button>
        <button
          @click="$emit('send-to-back')"
          class="tool-button"
          title="Send to Back"
        >
          <svg
            width="24"
            height="24"
            viewBox="0 0 402 390"
            preserveAspectRatio="xMidYMid meet"
          >
            <g transform="rotate(180, 201, 195)">
              <g
                transform="translate(0,390) scale(0.1,-0.1)"
                fill="currentColor"
              >
                <path
                  d="M1890 3507 c-41 -10 -70 -36 -300 -264 l-255 -252 2 -52 c2 -72 32 -103 103 -103 l51 0 175 175 c139 139 176 171 184 159 6 -9 10 -283 10 -706 0 -756 -1 -738 59 -775 40 -24 68 -24 105 0 57 38 55 9 56 769 0 600 2 703 14 708 9 4 68 -48 163 -144 81 -82 167 -160 190 -171 74 -39 143 -8 157 70 4 20 2 48 -4 63 -10 27 -408 432 -470 478 -70 53 -145 67 -240 45z"
                />
                <path
                  d="M2424 2477 c-2 -7 -3 -62 -2 -121 l3 -108 65 -33 c36 -18 117 -57 180 -88 63 -31 175 -85 248 -121 74 -36 140 -66 147 -66 16 0 26 -25 19 -45 -4 -8 -14 -15 -23 -15 -10 0 -26 -7 -37 -15 -10 -8 -26 -15 -35 -15 -9 0 -22 -7 -29 -15 -7 -8 -20 -15 -30 -15 -10 0 -23 -7 -30 -15 -7 -8 -20 -15 -30 -15 -10 0 -23 -7 -30 -15 -7 -8 -20 -15 -30 -15 -10 0 -23 -7 -30 -15 -7 -8 -19 -15 -26 -15 -7 0 -159 -72 -336 -161 -178 -88 -351 -169 -385 -180 -62 -20 -64 -20 -125 0 -35 10 -263 118 -507 240 -244 122 -450 221 -456 221 -7 0 -18 6 -25 14 -6 8 -21 16 -33 18 -33 5 -30 49 3 59 14 4 161 75 328 158 l302 151 0 115 c0 114 0 115 -24 115 -13 0 -29 -7 -36 -15 -7 -8 -19 -15 -27 -15 -24 0 -867 -424 -885 -445 -32 -39 -42 -89 -27 -141 15 -51 43 -77 119 -112 105 -48 144 -67 188 -92 9 -6 24 -13 32 -16 8 -3 22 -10 30 -15 8 -5 22 -12 30 -15 8 -3 205 -100 436 -215 232 -115 429 -209 438 -209 9 0 28 -7 41 -16 38 -25 203 -22 282 5 49 16 853 406 913 442 8 5 22 12 30 15 8 3 56 25 105 50 50 24 95 44 101 44 7 0 17 7 24 15 7 8 20 15 30 15 26 0 85 65 100 110 16 47 1 106 -34 139 -18 17 -937 481 -952 481 -3 0 -7 -6 -10 -13z"
                />
                <path
                  d="M2976 1341 c-60 -31 -111 -62 -113 -68 -2 -5 48 -36 112 -67 65 -32 115 -63 113 -69 -2 -7 -139 -79 -304 -161 -164 -81 -306 -152 -314 -157 -8 -5 -22 -12 -30 -15 -8 -3 -22 -10 -30 -15 -8 -5 -22 -12 -30 -15 -8 -3 -22 -10 -30 -15 -8 -5 -22 -12 -30 -15 -23 -9 -203 -95 -220 -105 -38 -23 -119 -39 -147 -28 -14 5 -35 9 -48 9 -20 0 -54 13 -105 42 -8 4 -22 11 -30 14 -8 3 -22 10 -30 15 -8 5 -22 12 -30 15 -8 3 -22 10 -30 15 -8 5 -22 12 -30 15 -20 8 -197 94 -520 252 -146 72 -272 137 -279 146 -11 13 -8 17 21 29 112 48 206 100 202 110 -5 14 -207 117 -229 117 -21 0 -229 -104 -270 -136 -59 -45 -79 -110 -53 -171 26 -60 36 -66 413 -248 99 -48 239 -115 310 -150 72 -35 150 -73 175 -85 25 -11 52 -25 60 -30 8 -5 35 -18 60 -30 25 -11 52 -25 60 -29 34 -19 197 -96 230 -109 19 -7 70 -16 112 -19 96 -7 144 6 318 89 69 33 168 80 220 105 52 25 102 49 110 54 8 5 22 12 30 15 8 3 22 10 30 15 8 5 22 12 30 15 8 3 22 10 30 15 8 5 22 12 30 15 61 24 629 310 646 325 51 48 55 143 7 199 -22 27 -264 161 -298 166 -5 1 -59 -24 -119 -55z"
                />
              </g>
            </g>
          </svg>
          To Back
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "EditorTools",
  props: {
    selection: { type: Object, default: () => ({ type: null, item: null }) },
    selectedElement: {
      type: String,
      default: null,
    },
    canUndo: {
      type: Boolean,
      default: false,
    },
    canRedo: {
      type: Boolean,
      default: false,
    },
    canPaste: {
      type: Boolean,
      default: false,
    },
    canCopyCutDelete: {
      type: Boolean,
      default: false,
    },
  },
  emits: [
    "save-design",
    "clear-canvas",
    "undo",
    "redo",
    "cut",
    "copy",
    "paste",
    "delete-selected",
    "deselect-all",
    "align-element",
    "bring-forward",
    "send-backward",
    "bring-to-front",
    "send-to-back",
  ],
};
</script>

<style scoped>
.editor-tools-sidebar {
  width: 200px;
  background-color: #ffffff;
  padding: 20px;
  box-shadow: -2px 0 5px rgba(0, 0, 0, 0.1);
  overflow-y: auto;
  border-left: 1px solid #e0e0e0;
  flex-shrink: 0;
  font-family: "Inter", sans-serif;
}

.editor-tools-sidebar h2 {
  margin-top: 0;
  color: #333;
}

.tools-section {
  margin-bottom: 20px;
}

.category-title {
  font-weight: bold;
  font-size: 0.95em;
  margin-top: 0;
  margin-bottom: 10px;
  color: #333;
  padding-bottom: 5px;
  border-bottom: 1px solid #eee;
}

.button-grid-tools {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
}

.button-grid-tools.align-grid {
  grid-template-columns: repeat(3, 1fr);
}

.button-grid-tools.layer-grid {
  grid-template-columns: repeat(2, 1fr);
}

.tool-button {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  border: 1px solid #ccc;
  background-color: #f9f9f9;
  font-size: 0.8em;
  cursor: pointer;
  padding: 8px 5px;
  border-radius: 5px;
  transition: background-color 0.2s, border-color 0.2s;
  color: #333;
  min-height: 50px;
  text-align: center;
}

.tool-button svg {
  width: 20px;
  height: 20px;
}

.tool-button:hover:not(:disabled) {
  background-color: #f0f0f0;
  border-color: #4287f5;
}

.tool-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background-color: #f5f5f5;
}

.tool-button.save-button,
.tool-button.clear-all-button {
  width: 100%;
  flex-direction: row;
  gap: 8px;
  color: white;
  font-weight: bold;
}

.save-button {
  background-color: #28a745;
  border-color: #28a745;
}

.save-button:hover {
  background-color: #218838;
  border-color: #218838;
}

.clear-all-button {
  background-color: #dc3545;
  border-color: #dc3545;
}

.clear-all-button:hover:not(:disabled) {
  background-color: #c82333;
  border-color: #c82333;
}

.tool-button svg {
  fill: currentColor;
}
</style>
