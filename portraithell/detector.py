import math


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

        edges = []

        for y in range(0, img_h, 20):  # We'll check a band every 20 pixels.
            test_band = image.crop(box=(0, y, img_w, y + 1))
            
            streak = None  # A streak of black pixels, if there is one.
            for index, pixel in enumerate(test_band.getdata()):
                if sum(pixel) < 15:  # Close enough to black
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
                        if streak[0] == 0:
                            edges.append((streak[1] - streak[0]))

                        streak = None
            else:
                if streak:
                    portrait_bands += 1
                    edges.append((streak[1] - streak[0]))
                else:
                    landscape_bands += 1

        if portrait_bands == 0:
            return False

        if (float(landscape_bands) / float(portrait_bands)) > 0.25:
            return False

        mean_edge = sum(edges) / float(len(edges))
        if (mean_edge / float(img_w)) < 0.2:  # Vertical videos seem to have edges from 24%-28% of the thumb width
            return False

        edge_std_dev = math.sqrt(sum((edge - mean_edge) ** 2 for edge in edges) / len(edges))
        if edge_std_dev > 1:
            return False

        return True


                





