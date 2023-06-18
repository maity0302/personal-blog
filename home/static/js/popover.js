function _arrayLikeToArray(arr, len) {
  if (len == null || len > arr.length) len = arr.length;
  for (var i = 0, arr2 = new Array(len); i < len; i++) arr2[i] = arr[i];
  return arr2;
}
function _arrayWithoutHoles(arr) {
  if (Array.isArray(arr)) return _arrayLikeToArray(arr);
}
function _iterableToArray(iter) {
  if (
    (typeof Symbol !== "undefined" && iter[Symbol.iterator] != null) ||
    iter["@@iterator"] != null
  )
    return Array.from(iter);
}
function _nonIterableSpread() {
  throw new TypeError(
    "Invalid attempt to spread non-iterable instance.\\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."
  );
}
function _toConsumableArray(arr) {
  return (
    _arrayWithoutHoles(arr) ||
    _iterableToArray(arr) ||
    _unsupportedIterableToArray(arr) ||
    _nonIterableSpread()
  );
}
function _unsupportedIterableToArray(o, minLen) {
  if (!o) return;
  if (typeof o === "string") return _arrayLikeToArray(o, minLen);
  var n = Object.prototype.toString.call(o).slice(8, -1);
  if (n === "Object" && o.constructor) n = o.constructor.name;
  if (n === "Map" || n === "Set") return Array.from(n);
  if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n))
    return _arrayLikeToArray(o, minLen);
}
import {
  computePosition,
  flip,
  inline,
  offset,
  shift,
} from "https://cdn.jsdelivr.net/npm/@floating-ui/dom@latest/+esm";
(function () {
  var triggers = document.querySelectorAll("[data-popover-target]");
  var popovers = document.querySelectorAll("[data-popover]");
  if (triggers && popovers) {
    Array.from(triggers).forEach(function (trigger) {
      return Array.from(popovers).forEach(function (popover) {
        if (trigger.dataset.popoverTarget === popover.dataset.popover) {
          var _popover_classList, _popover_classList1;
          var setPosition = function setPosition() {
            computePosition(trigger, popover, {
              placement: placement,
              middleware: [
                flip(),
                inline(),
                shift(),
                offset(Number(offsetValue)),
              ],
            }).then(function (param) {
              var x = param.x,
                y = param.y;
              Object.assign(popover.style, {
                top: "".concat(y, "px"),
                left: "".concat(x, "px"),
              });
            });
          };
          var mountPopover = function mountPopover() {
            var _popover_classList, _popover_classList1;
            setPosition();
            (_popover_classList = popover.classList).remove.apply(
              _popover_classList,
              _toConsumableArray(unmountClasses)
            );
            (_popover_classList1 = popover.classList).add.apply(
              _popover_classList1,
              _toConsumableArray(mountClasses)
            );
          };
          var unmountPopover = function unmountPopover() {
            var _popover_classList, _popover_classList1;
            setPosition();
            (_popover_classList = popover.classList).remove.apply(
              _popover_classList,
              _toConsumableArray(mountClasses)
            );
            (_popover_classList1 = popover.classList).add.apply(
              _popover_classList1,
              _toConsumableArray(unmountClasses)
            );
          };
          var closeAll = function closeAll() {
            Array.from(popovers).forEach(function (el) {
              return el.className.includes(mountValue)
                ? unmountPopover()
                : null;
            });
          };
          var placement = popover.dataset.popoverPlacement || "top";
          var offsetValue = popover.dataset.popoverOffset || 5;
          var mountValue = popover.dataset.popoverMount || "opacity-1";
          var unmountValue =
            popover.dataset.popoverUnmount || "pointer-events-none opacity-0";
          var transitionValue =
            popover.dataset.popoverTransition ||
            "transition-opacity duration-300";
          var mountClasses = mountValue.split(" ");
          var unmountClasses = unmountValue.split(" ");
          var transitionClasses = transitionValue.split(" ");
          (_popover_classList = popover.classList).add.apply(
            _popover_classList,
            _toConsumableArray(unmountClasses)
          );
          if (!popover.hasAttribute("tabindex"))
            popover.setAttribute("tabindex", 0);
          if (transitionValue !== "false")
            (_popover_classList1 = popover.classList).add.apply(
              _popover_classList1,
              _toConsumableArray(transitionClasses)
            );
          trigger.addEventListener("click", function (param) {
            var target = param.target;
            if (popover.className.includes(unmountValue)) {
              mountPopover();
            } else {
              Array.from(popovers).forEach(function (el) {
                var _target_dataset;
                if (
                  el.className.includes(mountValue) &&
                  (target === null || target === void 0
                    ? void 0
                    : (_target_dataset = target.dataset) === null ||
                      _target_dataset === void 0
                    ? void 0
                    : _target_dataset.popoverNested)
                ) {
                  var _el_classList, _el_classList1;
                  (_el_classList = el.classList).remove.apply(
                    _el_classList,
                    _toConsumableArray(mountClasses)
                  );
                  (_el_classList1 = el.classList).add.apply(
                    _el_classList1,
                    _toConsumableArray(unmountClasses)
                  );
                }
              });
              unmountPopover();
            }
          });
          document.addEventListener("click", function (param) {
            var target = param.target;
            var _target_dataset,
              _target_offsetParent,
              _target_offsetParent_dataset,
              _target_offsetParent1,
              _target_offsetParent_dataset1;
            if (
              !(target === null || target === void 0
                ? void 0
                : (_target_dataset = target.dataset) === null ||
                  _target_dataset === void 0
                ? void 0
                : _target_dataset.popover) &&
              !((_target_offsetParent = target.offsetParent) === null ||
              _target_offsetParent === void 0
                ? void 0
                : (_target_offsetParent_dataset =
                    _target_offsetParent.dataset) === null ||
                  _target_offsetParent_dataset === void 0
                ? void 0
                : _target_offsetParent_dataset.popover) &&
              !(target === null || target === void 0
                ? void 0
                : target.dataset.popoverTarget) &&
              !((_target_offsetParent1 = target.offsetParent) === null ||
              _target_offsetParent1 === void 0
                ? void 0
                : (_target_offsetParent_dataset1 =
                    _target_offsetParent1.dataset) === null ||
                  _target_offsetParent_dataset1 === void 0
                ? void 0
                : _target_offsetParent_dataset1.popoverTarget)
            )
              closeAll();
          });
          document.addEventListener("keyup", function (param) {
            var key = param.key;
            return key === "Escape" ? closeAll() : null;
          });
        }
      });
    });
  }
})();
