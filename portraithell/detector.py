class Detector(object):
    def detect(self, images):
        score = sum(map(self.check_image, images))
        return score >= 0.5 * len(images)

    def check_image(self, image):
        img_w, img_h = image.size
        check_ratios = (3. / 4., 9. / 16.)
        for check_ratio in check_ratios:
            potential_gap = int(0.5 * img_h * check_ratio) - 1  # minus fudge
            bounds = (
                (0, 0, potential_gap, img_h),
                (img_w - potential_gap, 0, img_w, img_h)
            )
            both_black = True
            for box in bounds:
                both_black = both_black and self.is_all_black(image.crop(box))
            if both_black:
                return True
        return False

    def is_all_black(self, image):
        extrema = image.getextrema()
        return extrema == ((0, 0), (0, 0), (0, 0))


class BandDetector(Detector):

    def check_image(self, image):
        img_w, img_h = image.size

        portrait_bands = 0
        landscape_bands = 0

        for y in range(0, img_h, 20):  # We'll check a band every 20 pixels.
            test_band = image.crop(box=(0, y, img_w, y + 1))
            
            streak = None  # A streak of black pixels, if there is one.
            for index, pixel in enumerate(test_band.getdata()):
                if pixel == (0, 0, 0):
                    if streak:
                        streak[1] = index
                    else:
                        streak = [index, index]

                    if (streak[1] - streak[0]) > (img_w / 2):
                        landscape_bands += 1
                        break
                else:
                    if streak:
                        # Looks like the streak is broken.
                        if index < (img_w / 4):
                            # I don't think this band is legit, let's break.
                            landscape_bands += 1
                            break
                        streak = None
            else:
                if streak and (streak[1] - streak[0]) < (img_w / 4):
                    portrait_bands += 1
                else:
                    landscape_bands += 1

        if portrait_bands == 0:
            return False

        if (float(landscape_bands) / float(portrait_bands)) > 0.25:
            return False
            
        return True


                





